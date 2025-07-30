import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from typing import List, Optional, Tuple, Dict
import functools

class DecoderRegistry:
    _decoders: Dict[str, callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func):
            cls._decoders[name] = func
            return func
        return decorator

    @classmethod
    def get(cls, name: str):
        if name not in cls._decoders:
            available = list(cls._decoders.keys())
            raise ValueError(f"Unknown decoder '{name}'. Available: {available}")
        return cls._decoders[name]

    @classmethod
    def available(cls) -> List[str]:
        return sorted(cls._decoders.keys())


def conv_block(x: tf.Tensor, filters: int, kernel_size: int = 3, activation: str = "relu",
               use_batchnorm: bool = True, dropout_rate: float = 0.0, name: str = "conv_block") -> tf.Tensor:
    x = layers.Conv2D(filters, kernel_size, padding="same", use_bias=not use_batchnorm, name=f"{name}_conv1")(x)
    if use_batchnorm:
        x = layers.BatchNormalization(name=f"{name}_bn1")(x)
    x = layers.Activation(activation, name=f"{name}_act1")(x)
    if dropout_rate > 0:
        x = layers.Dropout(dropout_rate, name=f"{name}_dropout1")(x)
    
    x = layers.Conv2D(filters, kernel_size, padding="same", use_bias=not use_batchnorm, name=f"{name}_conv2")(x)
    if use_batchnorm:
        x = layers.BatchNormalization(name=f"{name}_bn2")(x)
    x = layers.Activation(activation, name=f"{name}_act2")(x)
    if dropout_rate > 0:
        x = layers.Dropout(dropout_rate, name=f"{name}_dropout2")(x)
    return x

def _make_conv_block(filters: int,
                     use_batchnorm: bool,
                     dropout_rate: float,
                     name: str) -> keras.Sequential:
    blk = []
    
    blk.append(layers.Conv2D(filters, 3, padding="same",
                             use_bias=not use_batchnorm,
                             name=f"{name}_conv1"))
    if use_batchnorm:
        blk.append(layers.BatchNormalization(name=f"{name}_bn1"))
    blk.append(layers.Activation("relu", name=f"{name}_act1"))
    if dropout_rate:
        blk.append(layers.Dropout(dropout_rate, name=f"{name}_drop1"))
    
    blk.append(layers.Conv2D(filters, 3, padding="same",
                             use_bias=not use_batchnorm,
                             name=f"{name}_conv2"))
    if use_batchnorm:
        blk.append(layers.BatchNormalization(name=f"{name}_bn2"))
    blk.append(layers.Activation("relu", name=f"{name}_act2"))
    if dropout_rate:
        blk.append(layers.Dropout(dropout_rate, name=f"{name}_drop2"))

    return keras.Sequential(blk, name=name)

def upsample_block(x: tf.Tensor, filters: int, size: Tuple[int, int] = (2, 2), method: str = "bilinear",
                   use_batchnorm: bool = True, name: str = "upsample") -> tf.Tensor:
    if method == "conv_transpose":
        x = layers.Conv2DTranspose(
            filters, kernel_size=size, strides=size, 
            padding="same", use_bias=not use_batchnorm, 
            name=f"{name}_conv_transpose"
        )(x)
        if use_batchnorm:
            x = layers.BatchNormalization(name=f"{name}_bn")(x)
        x = layers.Activation("relu", name=f"{name}_relu")(x)
    else:
        x = layers.UpSampling2D(
            size=size, interpolation=method, 
            name=f"{name}_upsample"
        )(x)
        x = layers.Conv2D(
            filters, 1, padding="same", 
            use_bias=not use_batchnorm, name=f"{name}_conv"
        )(x)
        if use_batchnorm:
            x = layers.BatchNormalization(name=f"{name}_bn")(x)
        x = layers.Activation("relu", name=f"{name}_relu")(x)
    return x



class UNet(keras.Model):
    def __init__(self, num_encoder_levels: int, num_classes: int = 1,
                 decoder_filters: List[int] = [256, 128, 64, 32, 16],
                 upsample_method: str = "bilinear", use_batchnorm: bool = True,
                 dropout_rate: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        
        if len(decoder_filters) != num_encoder_levels:
            raise ValueError(
                f"decoder_filters length ({len(decoder_filters)}) "
                f"must match num_encoder_levels ({num_encoder_levels})"
            )
        
        self.num_encoder_levels = num_encoder_levels
        self.num_classes = num_classes
        self.decoder_filters = decoder_filters
        self.upsample_method = upsample_method
        self.use_batchnorm = use_batchnorm
        self.dropout_rate = dropout_rate

        self.upsample_layers = []
        self.conv_blocks = []
        for i, filters in enumerate(decoder_filters):
            self.upsample_layers.append(
                keras.Sequential([
                    layers.UpSampling2D(size=(2,2), interpolation=upsample_method, name=f"decoder_upsample_{i}"),
                    layers.Conv2D(filters, 1, padding="same", use_bias=not use_batchnorm, name=f"decoder_upsample_{i}_conv"),
                    layers.BatchNormalization(name=f"decoder_upsample_{i}_bn") if use_batchnorm else layers.Layer(),
                    layers.Activation("relu", name=f"decoder_upsample_{i}_relu")
                ], name=f"upsample_block_{i}")
            )
            self.conv_blocks.append(
                keras.Sequential([
                    layers.Conv2D(filters, 3, padding="same", use_bias=not use_batchnorm, name=f"decoder_block_{i}_conv1"),
                    layers.BatchNormalization(name=f"decoder_block_{i}_bn1") if use_batchnorm else layers.Layer(),
                    layers.Activation("relu", name=f"decoder_block_{i}_act1"),
                    layers.Conv2D(filters, 3, padding="same", use_bias=not use_batchnorm, name=f"decoder_block_{i}_conv2"),
                    layers.BatchNormalization(name=f"decoder_block_{i}_bn2") if use_batchnorm else layers.Layer(),
                    layers.Activation("relu", name=f"decoder_block_{i}_act2"),
                ], name=f"conv_block_{i}")
            )

        self.final_conv = layers.Conv2D(
            num_classes, 1, padding="same", activation=None, name="final_conv"
        )

    def call(self, encoder_outputs: List[tf.Tensor], training: Optional[bool] = None, target_size=None) -> tf.Tensor:
        if len(encoder_outputs) != self.num_encoder_levels:
            raise ValueError(
                f"Expected {self.num_encoder_levels} encoder outputs, got {len(encoder_outputs)}"
            )
        
        skips = list(reversed(encoder_outputs[:-1]))
        x = encoder_outputs[-1]
        
        for i, (upsample_layer, conv_block_layer) in enumerate(zip(self.upsample_layers, self.conv_blocks)):
            x = upsample_layer(x, training=training)
            
            if i < len(skips):
                skip = skips[i]
                
                if x.shape[1:3] != skip.shape[1:3]:
                    x = tf.image.resize(x, tf.shape(skip)[1:3], method="bilinear")
                
                x = layers.Concatenate(axis=-1, name=f"skip_concat_{i}")([x, skip])
            
            x = conv_block_layer(x, training=training)
        
        output = self.final_conv(x)
        if target_size is not None:
            output = tf.image.resize(output, target_size, method="bilinear")
        return output

@DecoderRegistry.register("unet")
def build_unet_decoder(num_encoder_levels: int, num_classes: int = 1, **kwargs) -> keras.Model:
    return UNet(num_encoder_levels=num_encoder_levels, num_classes=num_classes, **kwargs)



class UNetPlusPlus(keras.Model):
    def __init__(self,
                 num_encoder_levels: int,
                 num_classes: int = 1,
                 decoder_filters: List[int] = (256, 128, 64, 32, 16),
                 deep_supervision: bool = False,
                 use_batchnorm: bool = True,
                 dropout_rate: float = 0.0,
                 **kwargs):
        super().__init__(**kwargs)

        if len(decoder_filters) != num_encoder_levels:
            raise ValueError("`decoder_filters` length must equal "
                             "`num_encoder_levels`")

        self.L                 = num_encoder_levels
        self.num_classes       = num_classes
        self.decoder_filters   = decoder_filters
        self.deep_supervision  = deep_supervision
        self.use_batchnorm     = use_batchnorm
        self.dropout_rate      = dropout_rate

        self.conv_blocks: Dict[Tuple[int, int], keras.Sequential] = {}
        for j in range(1, self.L):          # columns
            for i in range(self.L - j):     # rows
                name = f"conv_block_{i}_{j}"
                filters = decoder_filters[i]
                self.conv_blocks[(i, j)] = _make_conv_block(
                    filters, use_batchnorm, dropout_rate, name
                )

        if self.deep_supervision:
            self.ds_heads = [
                layers.Conv2D(num_classes, 1, padding="same",
                              name=f"ds_head_{j}")
                for j in range(1, self.L)
            ]

        self.final_conv = layers.Conv2D(
            num_classes, 1, padding="same", activation=None, name="final_conv"
        )

    def call(self,
             encoder_outputs: List[tf.Tensor],
             training: bool = None,
             target_size=None) -> tf.Tensor:

        if len(encoder_outputs) != self.L:
            raise ValueError(f"Expected {self.L} encoder feature maps, "
                             f"got {len(encoder_outputs)}")

        grid: Dict[Tuple[int, int], tf.Tensor] = {
            (i, 0): feat for i, feat in enumerate(encoder_outputs)
        }

        for j in range(1, self.L):
            for i in range(self.L - j):
                inputs = []

                up = tf.image.resize(
                    grid[(i + 1, j - 1)],
                    size=tf.shape(grid[(i, j - 1)])[1:3],
                    method="bilinear"
                )
                inputs.append(up)

                for k in range(j):
                    inputs.append(grid[(i, k)])

                ref_hw = tf.shape(inputs[0])[1:3]
                inputs = [tf.image.resize(t, ref_hw, "bilinear")
                          for t in inputs]

                concat = layers.Concatenate(axis=-1,
                                            name=f"concat_{i}_{j}")(inputs)

                grid[(i, j)] = self.conv_blocks[(i, j)](
                    concat, training=training
                )

        if self.deep_supervision:
            logits_list = []
            for j in range(1, self.L):
                node = grid[(0, j)]
                logits = self.ds_heads[j - 1](node)
                logits = tf.image.resize(
                    logits, tf.shape(encoder_outputs[0])[1:3],
                    method="bilinear"
                )
                logits_list.append(logits)
            logits = tf.reduce_mean(tf.stack(logits_list, axis=0), axis=0)
        else:
            logits = self.final_conv(grid[(0, self.L - 1)])

        if target_size is not None:
            logits = tf.image.resize(logits, target_size, "bilinear")

        return logits


@DecoderRegistry.register("unetplusplus")
def build_unetplusplus_decoder(num_encoder_levels: int, num_classes: int = 1, **kwargs) -> keras.Model:
    return UNetPlusPlus(num_encoder_levels=num_encoder_levels, num_classes=num_classes, **kwargs)



class ASPP(layers.Layer):
    def __init__(self, filters: int, rates: List[int], use_batchnorm: bool, dropout_rate: float, **kwargs):
        super().__init__(**kwargs)
        self.convs = []
        
        self.convs.append(
            layers.Conv2D(filters, 1, padding="same", use_bias=False, name="aspp_1x1")
        )
        
        for rate in rates:
            self.convs.append(
                layers.Conv2D(
                    filters, 3, padding="same", dilation_rate=rate,
                    use_bias=False, name=f"aspp_3x3_r{rate}"
                )
            )
        
        self.global_pool = layers.GlobalAveragePooling2D(name="aspp_pool")
        self.pool_conv = layers.Conv2D(filters, 1, use_bias=False, name="aspp_pool_conv")
        
        self.projection = layers.Conv2D(filters, 1, padding="same", use_bias=False, name="aspp_proj")
        self.dropout = layers.Dropout(dropout_rate, name="aspp_dropout")
        
        self.bns = []
        if use_batchnorm:
            for i in range(len(self.convs) + 1):
                self.bns.append(layers.BatchNormalization(name=f"aspp_bn_{i}"))

    def call(self, inputs, training=None):
        branches = []
        
        for i, conv in enumerate(self.convs):
            x = conv(inputs)
            if self.bns:
                x = self.bns[i](x, training=training)
            x = tf.nn.relu(x)
            branches.append(x)
        
        pool = self.global_pool(inputs)
        pool = tf.expand_dims(tf.expand_dims(pool, 1), 1)
        pool = self.pool_conv(pool)
        if self.bns:
            pool = self.bns[len(self.convs)](pool, training=training)
        pool = tf.nn.relu(pool)
        pool = tf.image.resize(pool, tf.shape(inputs)[1:3], method="bilinear")
        branches.append(pool)
        
        x = layers.Concatenate(axis=-1, name="aspp_concat")(branches)
        x = self.projection(x)
        if self.bns:
            x = self.bns[-1](x, training=training)
        x = tf.nn.relu(x)
        return self.dropout(x, training=training)

class DeepLabV3Plus(keras.Model):
    def __init__(self, num_encoder_levels: int, num_classes: int = 1,
                 aspp_filters: int = 256, decoder_filters: int = 256,
                 atrous_rates: List[int] = [6, 12, 18], low_level_index: int = 1,
                 use_batchnorm: bool = True, dropout_rate: float = 0.1, **kwargs):
        super().__init__(**kwargs)
        
        if low_level_index >= num_encoder_levels:
            raise ValueError(
                f"low_level_index ({low_level_index}) must be < num_encoder_levels ({num_encoder_levels})"
            )
        
        self.num_encoder_levels = num_encoder_levels
        self.num_classes = num_classes
        self.low_level_index = low_level_index
        self.use_batchnorm = use_batchnorm
        
        self.aspp = ASPP(
            filters=aspp_filters,
            rates=atrous_rates,
            use_batchnorm=use_batchnorm,
            dropout_rate=dropout_rate,
            name="aspp"
        )
        
        self.low_level_conv = layers.Conv2D(
            48, 1, padding="same", use_bias=not use_batchnorm, name="low_level_conv"
        )
        if use_batchnorm:
            self.low_level_bn = layers.BatchNormalization(name="low_level_bn")
        
        self.decoder_conv1 = layers.Conv2D(
            decoder_filters, 3, padding="same", use_bias=not use_batchnorm, name="decoder_conv1"
        )
        if use_batchnorm:
            self.decoder_bn1 = layers.BatchNormalization(name="decoder_bn1")
            
        self.decoder_conv2 = layers.Conv2D(
            decoder_filters, 3, padding="same", use_bias=not use_batchnorm, name="decoder_conv2"
        )
        if use_batchnorm:
            self.decoder_bn2 = layers.BatchNormalization(name="decoder_bn2")
        
        self.final_conv = layers.Conv2D(
            num_classes, 1, padding="same", activation=None, name="final_conv"
        )

    def call(self, encoder_outputs: List[tf.Tensor], training: Optional[bool] = None, target_size=None) -> tf.Tensor:
        if len(encoder_outputs) != self.num_encoder_levels:
            raise ValueError(
                f"Expected {self.num_encoder_levels} encoder outputs, got {len(encoder_outputs)}"
            )
        
        high_level = encoder_outputs[-1]
        x = self.aspp(high_level, training=training)
        
        low_level = encoder_outputs[self.low_level_index]
        low_level = self.low_level_conv(low_level)
        if self.use_batchnorm:
            low_level = self.low_level_bn(low_level, training=training)
        low_level = tf.nn.relu(low_level)
        
        x = tf.image.resize(x, tf.shape(low_level)[1:3], method="bilinear")
        
        x = layers.Concatenate(axis=-1, name="decoder_concat")([x, low_level])
        
        x = self.decoder_conv1(x)
        if self.use_batchnorm:
            x = self.decoder_bn1(x, training=training)
        x = tf.nn.relu(x)
        
        x = self.decoder_conv2(x)
        if self.use_batchnorm:
            x = self.decoder_bn2(x, training=training)
        x = tf.nn.relu(x)
        
        output = self.final_conv(x)
        if target_size is not None:
            output = tf.image.resize(output, target_size, method="bilinear")
        return output

@DecoderRegistry.register("deeplabv3plus")
def build_deeplabv3plus_decoder(num_encoder_levels: int, num_classes: int = 1, **kwargs) -> keras.Model:
    if num_encoder_levels < 2:
        raise ValueError(f"DeepLabV3+ requires ≥2 feature levels, got {num_encoder_levels}")
    return DeepLabV3Plus(num_encoder_levels=num_encoder_levels, num_classes=num_classes, **kwargs)



def get_decoder(name: str, num_encoder_levels: int, num_classes: int = 1, **kwargs) -> keras.Model:
    builder = DecoderRegistry.get(name)
    return builder(num_encoder_levels=num_encoder_levels, num_classes=num_classes, **kwargs)


def list_decoders() -> List[str]:
    return DecoderRegistry.available()

def get_decoder_info(name: str) -> dict:
    info = {
        "unet": {
            "description": "Classic U-Net with skip connections",
            "paper": "U-Net: Convolutional Networks for Biomedical Image Segmentation",
            "strengths": ["Simple architecture", "Effective for medical images", "Fast training"],
            "use_cases": ["Medical image segmentation", "Cell tracking", "General segmentation tasks"],
            "min_encoder_levels": 2
        },
        "unetplusplus": {
            "description": "Nested U-Net++ with dense skip connections",
            "paper": "UNet++: A Nested U-Net Architecture for Medical Image Segmentation",
            "strengths": ["Improved gradient flow", "Deep supervision", "Better feature fusion"],
            "use_cases": ["Detailed segmentation", "Medical imaging", "Small object detection"],
            "min_encoder_levels": 3
        },
        "deeplabv3plus": {
            "description": "DeepLabV3+ with ASPP for multi-scale feature extraction",
            "paper": "Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation",
            "strengths": ["Handles multiple scales", "Effective for objects at different sizes", "State-of-the-art performance"],
            "use_cases": ["Autonomous driving", "Scene parsing", "High-resolution segmentation"],
            "min_encoder_levels": 2
        }
    }
    
    if name not in info:
        available = list(info.keys())
        raise ValueError(f"Unknown decoder '{name}'. Available: {available}")
    
    return info[name]