ку
░Ж
B
AssignVariableOp
resource
value"dtype"
dtypetypeИ
~
BiasAdd

value"T	
bias"T
output"T" 
Ttype:
2	"-
data_formatstringNHWC:
NHWCNCHW
8
Const
output"dtype"
valuetensor"
dtypetype
.
Identity

input"T
output"T"	
Ttype
q
MatMul
a"T
b"T
product"T"
transpose_abool( "
transpose_bbool( "
Ttype:

2	
e
MergeV2Checkpoints
checkpoint_prefixes
destination_prefix"
delete_old_dirsbool(И

NoOp
M
Pack
values"T*N
output"T"
Nint(0"	
Ttype"
axisint 
C
Placeholder
output"dtype"
dtypetype"
shapeshape:
@
ReadVariableOp
resource
value"dtype"
dtypetypeИ
E
Relu
features"T
activations"T"
Ttype:
2	
o
	RestoreV2

prefix
tensor_names
shape_and_slices
tensors2dtypes"
dtypes
list(type)(0И
l
SaveV2

prefix
tensor_names
shape_and_slices
tensors2dtypes"
dtypes
list(type)(0И
?
Select
	condition

t"T
e"T
output"T"	
Ttype
H
ShardedFilename
basename	
shard

num_shards
filename
┴
StatefulPartitionedCall
args2Tin
output2Tout"
Tin
list(type)("
Tout
list(type)("	
ffunc"
configstring "
config_protostring "
executor_typestring Ии
@
StaticRegexFullMatch	
input

output
"
patternstring
N

StringJoin
inputs*N

output"
Nint(0"
	separatorstring 
Ц
VarHandleOp
resource"
	containerstring "
shared_namestring "
dtypetype"
shapeshape"#
allowed_deviceslist(string)
 И"serve*2.7.02v2.7.0-0-gc256c071bb28╢х
Й
input_784_to_32/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape:	Р *'
shared_nameinput_784_to_32/kernel
В
*input_784_to_32/kernel/Read/ReadVariableOpReadVariableOpinput_784_to_32/kernel*
_output_shapes
:	Р *
dtype0
А
input_784_to_32/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape: *%
shared_nameinput_784_to_32/bias
y
(input_784_to_32/bias/Read/ReadVariableOpReadVariableOpinput_784_to_32/bias*
_output_shapes
: *
dtype0
И
hidden_linear_1/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *'
shared_namehidden_linear_1/kernel
Б
*hidden_linear_1/kernel/Read/ReadVariableOpReadVariableOphidden_linear_1/kernel*
_output_shapes

:  *
dtype0
А
hidden_linear_1/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape: *%
shared_namehidden_linear_1/bias
y
(hidden_linear_1/bias/Read/ReadVariableOpReadVariableOphidden_linear_1/bias*
_output_shapes
: *
dtype0
И
hidden_linear_2/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *'
shared_namehidden_linear_2/kernel
Б
*hidden_linear_2/kernel/Read/ReadVariableOpReadVariableOphidden_linear_2/kernel*
_output_shapes

:  *
dtype0
А
hidden_linear_2/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape: *%
shared_namehidden_linear_2/bias
y
(hidden_linear_2/bias/Read/ReadVariableOpReadVariableOphidden_linear_2/bias*
_output_shapes
: *
dtype0
И
hidden_linear_3/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *'
shared_namehidden_linear_3/kernel
Б
*hidden_linear_3/kernel/Read/ReadVariableOpReadVariableOphidden_linear_3/kernel*
_output_shapes

:  *
dtype0
А
hidden_linear_3/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape: *%
shared_namehidden_linear_3/bias
y
(hidden_linear_3/bias/Read/ReadVariableOpReadVariableOphidden_linear_3/bias*
_output_shapes
: *
dtype0
t
Dense/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
: 
*
shared_nameDense/kernel
m
 Dense/kernel/Read/ReadVariableOpReadVariableOpDense/kernel*
_output_shapes

: 
*
dtype0
l

Dense/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape:
*
shared_name
Dense/bias
e
Dense/bias/Read/ReadVariableOpReadVariableOp
Dense/bias*
_output_shapes
:
*
dtype0
f
	Adam/iterVarHandleOp*
_output_shapes
: *
dtype0	*
shape: *
shared_name	Adam/iter
_
Adam/iter/Read/ReadVariableOpReadVariableOp	Adam/iter*
_output_shapes
: *
dtype0	
j
Adam/beta_1VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_nameAdam/beta_1
c
Adam/beta_1/Read/ReadVariableOpReadVariableOpAdam/beta_1*
_output_shapes
: *
dtype0
j
Adam/beta_2VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_nameAdam/beta_2
c
Adam/beta_2/Read/ReadVariableOpReadVariableOpAdam/beta_2*
_output_shapes
: *
dtype0
h

Adam/decayVarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_name
Adam/decay
a
Adam/decay/Read/ReadVariableOpReadVariableOp
Adam/decay*
_output_shapes
: *
dtype0
x
Adam/learning_rateVarHandleOp*
_output_shapes
: *
dtype0*
shape: *#
shared_nameAdam/learning_rate
q
&Adam/learning_rate/Read/ReadVariableOpReadVariableOpAdam/learning_rate*
_output_shapes
: *
dtype0
^
totalVarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_nametotal
W
total/Read/ReadVariableOpReadVariableOptotal*
_output_shapes
: *
dtype0
^
countVarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_namecount
W
count/Read/ReadVariableOpReadVariableOpcount*
_output_shapes
: *
dtype0
b
total_1VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_name	total_1
[
total_1/Read/ReadVariableOpReadVariableOptotal_1*
_output_shapes
: *
dtype0
b
count_1VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_name	count_1
[
count_1/Read/ReadVariableOpReadVariableOpcount_1*
_output_shapes
: *
dtype0
Ч
Adam/input_784_to_32/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:	Р *.
shared_nameAdam/input_784_to_32/kernel/m
Р
1Adam/input_784_to_32/kernel/m/Read/ReadVariableOpReadVariableOpAdam/input_784_to_32/kernel/m*
_output_shapes
:	Р *
dtype0
О
Adam/input_784_to_32/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/input_784_to_32/bias/m
З
/Adam/input_784_to_32/bias/m/Read/ReadVariableOpReadVariableOpAdam/input_784_to_32/bias/m*
_output_shapes
: *
dtype0
Ц
Adam/hidden_linear_1/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *.
shared_nameAdam/hidden_linear_1/kernel/m
П
1Adam/hidden_linear_1/kernel/m/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_1/kernel/m*
_output_shapes

:  *
dtype0
О
Adam/hidden_linear_1/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/hidden_linear_1/bias/m
З
/Adam/hidden_linear_1/bias/m/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_1/bias/m*
_output_shapes
: *
dtype0
Ц
Adam/hidden_linear_2/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *.
shared_nameAdam/hidden_linear_2/kernel/m
П
1Adam/hidden_linear_2/kernel/m/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_2/kernel/m*
_output_shapes

:  *
dtype0
О
Adam/hidden_linear_2/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/hidden_linear_2/bias/m
З
/Adam/hidden_linear_2/bias/m/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_2/bias/m*
_output_shapes
: *
dtype0
Ц
Adam/hidden_linear_3/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *.
shared_nameAdam/hidden_linear_3/kernel/m
П
1Adam/hidden_linear_3/kernel/m/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_3/kernel/m*
_output_shapes

:  *
dtype0
О
Adam/hidden_linear_3/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/hidden_linear_3/bias/m
З
/Adam/hidden_linear_3/bias/m/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_3/bias/m*
_output_shapes
: *
dtype0
В
Adam/Dense/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
: 
*$
shared_nameAdam/Dense/kernel/m
{
'Adam/Dense/kernel/m/Read/ReadVariableOpReadVariableOpAdam/Dense/kernel/m*
_output_shapes

: 
*
dtype0
z
Adam/Dense/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:
*"
shared_nameAdam/Dense/bias/m
s
%Adam/Dense/bias/m/Read/ReadVariableOpReadVariableOpAdam/Dense/bias/m*
_output_shapes
:
*
dtype0
Ч
Adam/input_784_to_32/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:	Р *.
shared_nameAdam/input_784_to_32/kernel/v
Р
1Adam/input_784_to_32/kernel/v/Read/ReadVariableOpReadVariableOpAdam/input_784_to_32/kernel/v*
_output_shapes
:	Р *
dtype0
О
Adam/input_784_to_32/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/input_784_to_32/bias/v
З
/Adam/input_784_to_32/bias/v/Read/ReadVariableOpReadVariableOpAdam/input_784_to_32/bias/v*
_output_shapes
: *
dtype0
Ц
Adam/hidden_linear_1/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *.
shared_nameAdam/hidden_linear_1/kernel/v
П
1Adam/hidden_linear_1/kernel/v/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_1/kernel/v*
_output_shapes

:  *
dtype0
О
Adam/hidden_linear_1/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/hidden_linear_1/bias/v
З
/Adam/hidden_linear_1/bias/v/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_1/bias/v*
_output_shapes
: *
dtype0
Ц
Adam/hidden_linear_2/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *.
shared_nameAdam/hidden_linear_2/kernel/v
П
1Adam/hidden_linear_2/kernel/v/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_2/kernel/v*
_output_shapes

:  *
dtype0
О
Adam/hidden_linear_2/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/hidden_linear_2/bias/v
З
/Adam/hidden_linear_2/bias/v/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_2/bias/v*
_output_shapes
: *
dtype0
Ц
Adam/hidden_linear_3/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:  *.
shared_nameAdam/hidden_linear_3/kernel/v
П
1Adam/hidden_linear_3/kernel/v/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_3/kernel/v*
_output_shapes

:  *
dtype0
О
Adam/hidden_linear_3/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape: *,
shared_nameAdam/hidden_linear_3/bias/v
З
/Adam/hidden_linear_3/bias/v/Read/ReadVariableOpReadVariableOpAdam/hidden_linear_3/bias/v*
_output_shapes
: *
dtype0
В
Adam/Dense/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
: 
*$
shared_nameAdam/Dense/kernel/v
{
'Adam/Dense/kernel/v/Read/ReadVariableOpReadVariableOpAdam/Dense/kernel/v*
_output_shapes

: 
*
dtype0
z
Adam/Dense/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:
*"
shared_nameAdam/Dense/bias/v
s
%Adam/Dense/bias/v/Read/ReadVariableOpReadVariableOpAdam/Dense/bias/v*
_output_shapes
:
*
dtype0

NoOpNoOp
О8
ConstConst"/device:CPU:0*
_output_shapes
: *
dtype0*╔7
value┐7B╝7 B╡7
┤
layer_with_weights-0
layer-0
layer_with_weights-1
layer-1
layer_with_weights-2
layer-2
layer_with_weights-3
layer-3
layer_with_weights-4
layer-4
	optimizer
	variables
trainable_variables
	regularization_losses

	keras_api

signatures
h

kernel
bias
	variables
trainable_variables
regularization_losses
	keras_api
h

kernel
bias
	variables
trainable_variables
regularization_losses
	keras_api
h

kernel
bias
	variables
trainable_variables
regularization_losses
	keras_api
h

kernel
bias
 	variables
!trainable_variables
"regularization_losses
#	keras_api
h

$kernel
%bias
&	variables
'trainable_variables
(regularization_losses
)	keras_api
Ї
*iter

+beta_1

,beta_2
	-decay
.learning_ratemXmYmZm[m\m]m^m_$m`%mavbvcvdvevfvgvhvi$vj%vk
F
0
1
2
3
4
5
6
7
$8
%9
F
0
1
2
3
4
5
6
7
$8
%9
 
н
/non_trainable_variables

0layers
1metrics
2layer_regularization_losses
3layer_metrics
	variables
trainable_variables
	regularization_losses
 
b`
VARIABLE_VALUEinput_784_to_32/kernel6layer_with_weights-0/kernel/.ATTRIBUTES/VARIABLE_VALUE
^\
VARIABLE_VALUEinput_784_to_32/bias4layer_with_weights-0/bias/.ATTRIBUTES/VARIABLE_VALUE

0
1

0
1
 
н
4non_trainable_variables

5layers
6metrics
7layer_regularization_losses
8layer_metrics
	variables
trainable_variables
regularization_losses
b`
VARIABLE_VALUEhidden_linear_1/kernel6layer_with_weights-1/kernel/.ATTRIBUTES/VARIABLE_VALUE
^\
VARIABLE_VALUEhidden_linear_1/bias4layer_with_weights-1/bias/.ATTRIBUTES/VARIABLE_VALUE

0
1

0
1
 
н
9non_trainable_variables

:layers
;metrics
<layer_regularization_losses
=layer_metrics
	variables
trainable_variables
regularization_losses
b`
VARIABLE_VALUEhidden_linear_2/kernel6layer_with_weights-2/kernel/.ATTRIBUTES/VARIABLE_VALUE
^\
VARIABLE_VALUEhidden_linear_2/bias4layer_with_weights-2/bias/.ATTRIBUTES/VARIABLE_VALUE

0
1

0
1
 
н
>non_trainable_variables

?layers
@metrics
Alayer_regularization_losses
Blayer_metrics
	variables
trainable_variables
regularization_losses
b`
VARIABLE_VALUEhidden_linear_3/kernel6layer_with_weights-3/kernel/.ATTRIBUTES/VARIABLE_VALUE
^\
VARIABLE_VALUEhidden_linear_3/bias4layer_with_weights-3/bias/.ATTRIBUTES/VARIABLE_VALUE

0
1

0
1
 
н
Cnon_trainable_variables

Dlayers
Emetrics
Flayer_regularization_losses
Glayer_metrics
 	variables
!trainable_variables
"regularization_losses
XV
VARIABLE_VALUEDense/kernel6layer_with_weights-4/kernel/.ATTRIBUTES/VARIABLE_VALUE
TR
VARIABLE_VALUE
Dense/bias4layer_with_weights-4/bias/.ATTRIBUTES/VARIABLE_VALUE

$0
%1

$0
%1
 
н
Hnon_trainable_variables

Ilayers
Jmetrics
Klayer_regularization_losses
Llayer_metrics
&	variables
'trainable_variables
(regularization_losses
HF
VARIABLE_VALUE	Adam/iter)optimizer/iter/.ATTRIBUTES/VARIABLE_VALUE
LJ
VARIABLE_VALUEAdam/beta_1+optimizer/beta_1/.ATTRIBUTES/VARIABLE_VALUE
LJ
VARIABLE_VALUEAdam/beta_2+optimizer/beta_2/.ATTRIBUTES/VARIABLE_VALUE
JH
VARIABLE_VALUE
Adam/decay*optimizer/decay/.ATTRIBUTES/VARIABLE_VALUE
ZX
VARIABLE_VALUEAdam/learning_rate2optimizer/learning_rate/.ATTRIBUTES/VARIABLE_VALUE
 
#
0
1
2
3
4

M0
N1
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
4
	Ototal
	Pcount
Q	variables
R	keras_api
D
	Stotal
	Tcount
U
_fn_kwargs
V	variables
W	keras_api
OM
VARIABLE_VALUEtotal4keras_api/metrics/0/total/.ATTRIBUTES/VARIABLE_VALUE
OM
VARIABLE_VALUEcount4keras_api/metrics/0/count/.ATTRIBUTES/VARIABLE_VALUE

O0
P1

Q	variables
QO
VARIABLE_VALUEtotal_14keras_api/metrics/1/total/.ATTRIBUTES/VARIABLE_VALUE
QO
VARIABLE_VALUEcount_14keras_api/metrics/1/count/.ATTRIBUTES/VARIABLE_VALUE
 

S0
T1

V	variables
ЖГ
VARIABLE_VALUEAdam/input_784_to_32/kernel/mRlayer_with_weights-0/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/input_784_to_32/bias/mPlayer_with_weights-0/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/hidden_linear_1/kernel/mRlayer_with_weights-1/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/hidden_linear_1/bias/mPlayer_with_weights-1/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/hidden_linear_2/kernel/mRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/hidden_linear_2/bias/mPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/hidden_linear_3/kernel/mRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/hidden_linear_3/bias/mPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
{y
VARIABLE_VALUEAdam/Dense/kernel/mRlayer_with_weights-4/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
wu
VARIABLE_VALUEAdam/Dense/bias/mPlayer_with_weights-4/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/input_784_to_32/kernel/vRlayer_with_weights-0/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/input_784_to_32/bias/vPlayer_with_weights-0/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/hidden_linear_1/kernel/vRlayer_with_weights-1/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/hidden_linear_1/bias/vPlayer_with_weights-1/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/hidden_linear_2/kernel/vRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/hidden_linear_2/bias/vPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
ЖГ
VARIABLE_VALUEAdam/hidden_linear_3/kernel/vRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
Б
VARIABLE_VALUEAdam/hidden_linear_3/bias/vPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
{y
VARIABLE_VALUEAdam/Dense/kernel/vRlayer_with_weights-4/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
wu
VARIABLE_VALUEAdam/Dense/bias/vPlayer_with_weights-4/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE
|
serving_default_input_1Placeholder*(
_output_shapes
:         Р*
dtype0*
shape:         Р
Ъ
StatefulPartitionedCallStatefulPartitionedCallserving_default_input_1input_784_to_32/kernelinput_784_to_32/biashidden_linear_1/kernelhidden_linear_1/biashidden_linear_2/kernelhidden_linear_2/biashidden_linear_3/kernelhidden_linear_3/biasDense/kernel
Dense/bias*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*,
_read_only_resource_inputs

	
*0
config_proto 

CPU

GPU2*0J 8В *,
f'R%
#__inference_signature_wrapper_41253
O
saver_filenamePlaceholder*
_output_shapes
: *
dtype0*
shape: 
╖
StatefulPartitionedCall_1StatefulPartitionedCallsaver_filename*input_784_to_32/kernel/Read/ReadVariableOp(input_784_to_32/bias/Read/ReadVariableOp*hidden_linear_1/kernel/Read/ReadVariableOp(hidden_linear_1/bias/Read/ReadVariableOp*hidden_linear_2/kernel/Read/ReadVariableOp(hidden_linear_2/bias/Read/ReadVariableOp*hidden_linear_3/kernel/Read/ReadVariableOp(hidden_linear_3/bias/Read/ReadVariableOp Dense/kernel/Read/ReadVariableOpDense/bias/Read/ReadVariableOpAdam/iter/Read/ReadVariableOpAdam/beta_1/Read/ReadVariableOpAdam/beta_2/Read/ReadVariableOpAdam/decay/Read/ReadVariableOp&Adam/learning_rate/Read/ReadVariableOptotal/Read/ReadVariableOpcount/Read/ReadVariableOptotal_1/Read/ReadVariableOpcount_1/Read/ReadVariableOp1Adam/input_784_to_32/kernel/m/Read/ReadVariableOp/Adam/input_784_to_32/bias/m/Read/ReadVariableOp1Adam/hidden_linear_1/kernel/m/Read/ReadVariableOp/Adam/hidden_linear_1/bias/m/Read/ReadVariableOp1Adam/hidden_linear_2/kernel/m/Read/ReadVariableOp/Adam/hidden_linear_2/bias/m/Read/ReadVariableOp1Adam/hidden_linear_3/kernel/m/Read/ReadVariableOp/Adam/hidden_linear_3/bias/m/Read/ReadVariableOp'Adam/Dense/kernel/m/Read/ReadVariableOp%Adam/Dense/bias/m/Read/ReadVariableOp1Adam/input_784_to_32/kernel/v/Read/ReadVariableOp/Adam/input_784_to_32/bias/v/Read/ReadVariableOp1Adam/hidden_linear_1/kernel/v/Read/ReadVariableOp/Adam/hidden_linear_1/bias/v/Read/ReadVariableOp1Adam/hidden_linear_2/kernel/v/Read/ReadVariableOp/Adam/hidden_linear_2/bias/v/Read/ReadVariableOp1Adam/hidden_linear_3/kernel/v/Read/ReadVariableOp/Adam/hidden_linear_3/bias/v/Read/ReadVariableOp'Adam/Dense/kernel/v/Read/ReadVariableOp%Adam/Dense/bias/v/Read/ReadVariableOpConst*4
Tin-
+2)	*
Tout
2*
_collective_manager_ids
 *
_output_shapes
: * 
_read_only_resource_inputs
 *0
config_proto 

CPU

GPU2*0J 8В *'
f"R 
__inference__traced_save_41618
ж	
StatefulPartitionedCall_2StatefulPartitionedCallsaver_filenameinput_784_to_32/kernelinput_784_to_32/biashidden_linear_1/kernelhidden_linear_1/biashidden_linear_2/kernelhidden_linear_2/biashidden_linear_3/kernelhidden_linear_3/biasDense/kernel
Dense/bias	Adam/iterAdam/beta_1Adam/beta_2
Adam/decayAdam/learning_ratetotalcounttotal_1count_1Adam/input_784_to_32/kernel/mAdam/input_784_to_32/bias/mAdam/hidden_linear_1/kernel/mAdam/hidden_linear_1/bias/mAdam/hidden_linear_2/kernel/mAdam/hidden_linear_2/bias/mAdam/hidden_linear_3/kernel/mAdam/hidden_linear_3/bias/mAdam/Dense/kernel/mAdam/Dense/bias/mAdam/input_784_to_32/kernel/vAdam/input_784_to_32/bias/vAdam/hidden_linear_1/kernel/vAdam/hidden_linear_1/bias/vAdam/hidden_linear_2/kernel/vAdam/hidden_linear_2/bias/vAdam/hidden_linear_3/kernel/vAdam/hidden_linear_3/bias/vAdam/Dense/kernel/vAdam/Dense/bias/v*3
Tin,
*2(*
Tout
2*
_collective_manager_ids
 *
_output_shapes
: * 
_read_only_resource_inputs
 *0
config_proto 

CPU

GPU2*0J 8В **
f%R#
!__inference__traced_restore_41745Ъ└
Э

ё
*__inference_sequential_layer_call_fn_41008
input_1
unknown:	Р 
	unknown_0: 
	unknown_1:  
	unknown_2: 
	unknown_3:  
	unknown_4: 
	unknown_5:  
	unknown_6: 
	unknown_7: 

	unknown_8:

identityИвStatefulPartitionedCall╞
StatefulPartitionedCallStatefulPartitionedCallinput_1unknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*,
_read_only_resource_inputs

	
*0
config_proto 

CPU

GPU2*0J 8В *N
fIRG
E__inference_sequential_layer_call_and_return_conditional_losses_40985o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:Q M
(
_output_shapes
:         Р
!
_user_specified_name	input_1
е

№
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_40911

inputs1
matmul_readvariableop_resource:	Р -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpu
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes
:	Р *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*+
_input_shapes
:         Р: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
б

√
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_40962

inputs0
matmul_readvariableop_resource:  -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:  *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
р
а
E__inference_sequential_layer_call_and_return_conditional_losses_41191
input_1(
input_784_to_32_41165:	Р #
input_784_to_32_41167: '
hidden_linear_1_41170:  #
hidden_linear_1_41172: '
hidden_linear_2_41175:  #
hidden_linear_2_41177: '
hidden_linear_3_41180:  #
hidden_linear_3_41182: 
dense_41185: 

dense_41187:

identityИвDense/StatefulPartitionedCallв'hidden_linear_1/StatefulPartitionedCallв'hidden_linear_2/StatefulPartitionedCallв'hidden_linear_3/StatefulPartitionedCallв'input_784_to_32/StatefulPartitionedCallН
'input_784_to_32/StatefulPartitionedCallStatefulPartitionedCallinput_1input_784_to_32_41165input_784_to_32_41167*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_40911╢
'hidden_linear_1/StatefulPartitionedCallStatefulPartitionedCall0input_784_to_32/StatefulPartitionedCall:output:0hidden_linear_1_41170hidden_linear_1_41172*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_40928╢
'hidden_linear_2/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_1/StatefulPartitionedCall:output:0hidden_linear_2_41175hidden_linear_2_41177*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_40945╢
'hidden_linear_3/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_2/StatefulPartitionedCall:output:0hidden_linear_3_41180hidden_linear_3_41182*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_40962О
Dense/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_3/StatefulPartitionedCall:output:0dense_41185dense_41187*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *I
fDRB
@__inference_Dense_layer_call_and_return_conditional_losses_40978u
IdentityIdentity&Dense/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
О
NoOpNoOp^Dense/StatefulPartitionedCall(^hidden_linear_1/StatefulPartitionedCall(^hidden_linear_2/StatefulPartitionedCall(^hidden_linear_3/StatefulPartitionedCall(^input_784_to_32/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2>
Dense/StatefulPartitionedCallDense/StatefulPartitionedCall2R
'hidden_linear_1/StatefulPartitionedCall'hidden_linear_1/StatefulPartitionedCall2R
'hidden_linear_2/StatefulPartitionedCall'hidden_linear_2/StatefulPartitionedCall2R
'hidden_linear_3/StatefulPartitionedCall'hidden_linear_3/StatefulPartitionedCall2R
'input_784_to_32/StatefulPartitionedCall'input_784_to_32/StatefulPartitionedCall:Q M
(
_output_shapes
:         Р
!
_user_specified_name	input_1
и0
╫
E__inference_sequential_layer_call_and_return_conditional_losses_41379

inputsA
.input_784_to_32_matmul_readvariableop_resource:	Р =
/input_784_to_32_biasadd_readvariableop_resource: @
.hidden_linear_1_matmul_readvariableop_resource:  =
/hidden_linear_1_biasadd_readvariableop_resource: @
.hidden_linear_2_matmul_readvariableop_resource:  =
/hidden_linear_2_biasadd_readvariableop_resource: @
.hidden_linear_3_matmul_readvariableop_resource:  =
/hidden_linear_3_biasadd_readvariableop_resource: 6
$dense_matmul_readvariableop_resource: 
3
%dense_biasadd_readvariableop_resource:

identityИвDense/BiasAdd/ReadVariableOpвDense/MatMul/ReadVariableOpв&hidden_linear_1/BiasAdd/ReadVariableOpв%hidden_linear_1/MatMul/ReadVariableOpв&hidden_linear_2/BiasAdd/ReadVariableOpв%hidden_linear_2/MatMul/ReadVariableOpв&hidden_linear_3/BiasAdd/ReadVariableOpв%hidden_linear_3/MatMul/ReadVariableOpв&input_784_to_32/BiasAdd/ReadVariableOpв%input_784_to_32/MatMul/ReadVariableOpХ
%input_784_to_32/MatMul/ReadVariableOpReadVariableOp.input_784_to_32_matmul_readvariableop_resource*
_output_shapes
:	Р *
dtype0Й
input_784_to_32/MatMulMatMulinputs-input_784_to_32/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&input_784_to_32/BiasAdd/ReadVariableOpReadVariableOp/input_784_to_32_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
input_784_to_32/BiasAddBiasAdd input_784_to_32/MatMul:product:0.input_784_to_32/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
input_784_to_32/ReluRelu input_784_to_32/BiasAdd:output:0*
T0*'
_output_shapes
:          Ф
%hidden_linear_1/MatMul/ReadVariableOpReadVariableOp.hidden_linear_1_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0е
hidden_linear_1/MatMulMatMul"input_784_to_32/Relu:activations:0-hidden_linear_1/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&hidden_linear_1/BiasAdd/ReadVariableOpReadVariableOp/hidden_linear_1_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
hidden_linear_1/BiasAddBiasAdd hidden_linear_1/MatMul:product:0.hidden_linear_1/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
hidden_linear_1/ReluRelu hidden_linear_1/BiasAdd:output:0*
T0*'
_output_shapes
:          Ф
%hidden_linear_2/MatMul/ReadVariableOpReadVariableOp.hidden_linear_2_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0е
hidden_linear_2/MatMulMatMul"hidden_linear_1/Relu:activations:0-hidden_linear_2/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&hidden_linear_2/BiasAdd/ReadVariableOpReadVariableOp/hidden_linear_2_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
hidden_linear_2/BiasAddBiasAdd hidden_linear_2/MatMul:product:0.hidden_linear_2/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
hidden_linear_2/ReluRelu hidden_linear_2/BiasAdd:output:0*
T0*'
_output_shapes
:          Ф
%hidden_linear_3/MatMul/ReadVariableOpReadVariableOp.hidden_linear_3_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0е
hidden_linear_3/MatMulMatMul"hidden_linear_2/Relu:activations:0-hidden_linear_3/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&hidden_linear_3/BiasAdd/ReadVariableOpReadVariableOp/hidden_linear_3_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
hidden_linear_3/BiasAddBiasAdd hidden_linear_3/MatMul:product:0.hidden_linear_3/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
hidden_linear_3/ReluRelu hidden_linear_3/BiasAdd:output:0*
T0*'
_output_shapes
:          А
Dense/MatMul/ReadVariableOpReadVariableOp$dense_matmul_readvariableop_resource*
_output_shapes

: 
*
dtype0С
Dense/MatMulMatMul"hidden_linear_3/Relu:activations:0#Dense/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
~
Dense/BiasAdd/ReadVariableOpReadVariableOp%dense_biasadd_readvariableop_resource*
_output_shapes
:
*
dtype0И
Dense/BiasAddBiasAddDense/MatMul:product:0$Dense/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
e
IdentityIdentityDense/BiasAdd:output:0^NoOp*
T0*'
_output_shapes
:         
╟
NoOpNoOp^Dense/BiasAdd/ReadVariableOp^Dense/MatMul/ReadVariableOp'^hidden_linear_1/BiasAdd/ReadVariableOp&^hidden_linear_1/MatMul/ReadVariableOp'^hidden_linear_2/BiasAdd/ReadVariableOp&^hidden_linear_2/MatMul/ReadVariableOp'^hidden_linear_3/BiasAdd/ReadVariableOp&^hidden_linear_3/MatMul/ReadVariableOp'^input_784_to_32/BiasAdd/ReadVariableOp&^input_784_to_32/MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2<
Dense/BiasAdd/ReadVariableOpDense/BiasAdd/ReadVariableOp2:
Dense/MatMul/ReadVariableOpDense/MatMul/ReadVariableOp2P
&hidden_linear_1/BiasAdd/ReadVariableOp&hidden_linear_1/BiasAdd/ReadVariableOp2N
%hidden_linear_1/MatMul/ReadVariableOp%hidden_linear_1/MatMul/ReadVariableOp2P
&hidden_linear_2/BiasAdd/ReadVariableOp&hidden_linear_2/BiasAdd/ReadVariableOp2N
%hidden_linear_2/MatMul/ReadVariableOp%hidden_linear_2/MatMul/ReadVariableOp2P
&hidden_linear_3/BiasAdd/ReadVariableOp&hidden_linear_3/BiasAdd/ReadVariableOp2N
%hidden_linear_3/MatMul/ReadVariableOp%hidden_linear_3/MatMul/ReadVariableOp2P
&input_784_to_32/BiasAdd/ReadVariableOp&input_784_to_32/BiasAdd/ReadVariableOp2N
%input_784_to_32/MatMul/ReadVariableOp%input_784_to_32/MatMul/ReadVariableOp:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
б

√
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_41439

inputs0
matmul_readvariableop_resource:  -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:  *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
╤
Ь
/__inference_hidden_linear_2_layer_call_fn_41428

inputs
unknown:  
	unknown_0: 
identityИвStatefulPartitionedCallт
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_40945o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:          `
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
р
а
E__inference_sequential_layer_call_and_return_conditional_losses_41220
input_1(
input_784_to_32_41194:	Р #
input_784_to_32_41196: '
hidden_linear_1_41199:  #
hidden_linear_1_41201: '
hidden_linear_2_41204:  #
hidden_linear_2_41206: '
hidden_linear_3_41209:  #
hidden_linear_3_41211: 
dense_41214: 

dense_41216:

identityИвDense/StatefulPartitionedCallв'hidden_linear_1/StatefulPartitionedCallв'hidden_linear_2/StatefulPartitionedCallв'hidden_linear_3/StatefulPartitionedCallв'input_784_to_32/StatefulPartitionedCallН
'input_784_to_32/StatefulPartitionedCallStatefulPartitionedCallinput_1input_784_to_32_41194input_784_to_32_41196*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_40911╢
'hidden_linear_1/StatefulPartitionedCallStatefulPartitionedCall0input_784_to_32/StatefulPartitionedCall:output:0hidden_linear_1_41199hidden_linear_1_41201*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_40928╢
'hidden_linear_2/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_1/StatefulPartitionedCall:output:0hidden_linear_2_41204hidden_linear_2_41206*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_40945╢
'hidden_linear_3/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_2/StatefulPartitionedCall:output:0hidden_linear_3_41209hidden_linear_3_41211*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_40962О
Dense/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_3/StatefulPartitionedCall:output:0dense_41214dense_41216*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *I
fDRB
@__inference_Dense_layer_call_and_return_conditional_losses_40978u
IdentityIdentity&Dense/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
О
NoOpNoOp^Dense/StatefulPartitionedCall(^hidden_linear_1/StatefulPartitionedCall(^hidden_linear_2/StatefulPartitionedCall(^hidden_linear_3/StatefulPartitionedCall(^input_784_to_32/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2>
Dense/StatefulPartitionedCallDense/StatefulPartitionedCall2R
'hidden_linear_1/StatefulPartitionedCall'hidden_linear_1/StatefulPartitionedCall2R
'hidden_linear_2/StatefulPartitionedCall'hidden_linear_2/StatefulPartitionedCall2R
'hidden_linear_3/StatefulPartitionedCall'hidden_linear_3/StatefulPartitionedCall2R
'input_784_to_32/StatefulPartitionedCall'input_784_to_32/StatefulPartitionedCall:Q M
(
_output_shapes
:         Р
!
_user_specified_name	input_1
▌
Я
E__inference_sequential_layer_call_and_return_conditional_losses_40985

inputs(
input_784_to_32_40912:	Р #
input_784_to_32_40914: '
hidden_linear_1_40929:  #
hidden_linear_1_40931: '
hidden_linear_2_40946:  #
hidden_linear_2_40948: '
hidden_linear_3_40963:  #
hidden_linear_3_40965: 
dense_40979: 

dense_40981:

identityИвDense/StatefulPartitionedCallв'hidden_linear_1/StatefulPartitionedCallв'hidden_linear_2/StatefulPartitionedCallв'hidden_linear_3/StatefulPartitionedCallв'input_784_to_32/StatefulPartitionedCallМ
'input_784_to_32/StatefulPartitionedCallStatefulPartitionedCallinputsinput_784_to_32_40912input_784_to_32_40914*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_40911╢
'hidden_linear_1/StatefulPartitionedCallStatefulPartitionedCall0input_784_to_32/StatefulPartitionedCall:output:0hidden_linear_1_40929hidden_linear_1_40931*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_40928╢
'hidden_linear_2/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_1/StatefulPartitionedCall:output:0hidden_linear_2_40946hidden_linear_2_40948*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_40945╢
'hidden_linear_3/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_2/StatefulPartitionedCall:output:0hidden_linear_3_40963hidden_linear_3_40965*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_40962О
Dense/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_3/StatefulPartitionedCall:output:0dense_40979dense_40981*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *I
fDRB
@__inference_Dense_layer_call_and_return_conditional_losses_40978u
IdentityIdentity&Dense/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
О
NoOpNoOp^Dense/StatefulPartitionedCall(^hidden_linear_1/StatefulPartitionedCall(^hidden_linear_2/StatefulPartitionedCall(^hidden_linear_3/StatefulPartitionedCall(^input_784_to_32/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2>
Dense/StatefulPartitionedCallDense/StatefulPartitionedCall2R
'hidden_linear_1/StatefulPartitionedCall'hidden_linear_1/StatefulPartitionedCall2R
'hidden_linear_2/StatefulPartitionedCall'hidden_linear_2/StatefulPartitionedCall2R
'hidden_linear_3/StatefulPartitionedCall'hidden_linear_3/StatefulPartitionedCall2R
'input_784_to_32/StatefulPartitionedCall'input_784_to_32/StatefulPartitionedCall:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
и0
╫
E__inference_sequential_layer_call_and_return_conditional_losses_41341

inputsA
.input_784_to_32_matmul_readvariableop_resource:	Р =
/input_784_to_32_biasadd_readvariableop_resource: @
.hidden_linear_1_matmul_readvariableop_resource:  =
/hidden_linear_1_biasadd_readvariableop_resource: @
.hidden_linear_2_matmul_readvariableop_resource:  =
/hidden_linear_2_biasadd_readvariableop_resource: @
.hidden_linear_3_matmul_readvariableop_resource:  =
/hidden_linear_3_biasadd_readvariableop_resource: 6
$dense_matmul_readvariableop_resource: 
3
%dense_biasadd_readvariableop_resource:

identityИвDense/BiasAdd/ReadVariableOpвDense/MatMul/ReadVariableOpв&hidden_linear_1/BiasAdd/ReadVariableOpв%hidden_linear_1/MatMul/ReadVariableOpв&hidden_linear_2/BiasAdd/ReadVariableOpв%hidden_linear_2/MatMul/ReadVariableOpв&hidden_linear_3/BiasAdd/ReadVariableOpв%hidden_linear_3/MatMul/ReadVariableOpв&input_784_to_32/BiasAdd/ReadVariableOpв%input_784_to_32/MatMul/ReadVariableOpХ
%input_784_to_32/MatMul/ReadVariableOpReadVariableOp.input_784_to_32_matmul_readvariableop_resource*
_output_shapes
:	Р *
dtype0Й
input_784_to_32/MatMulMatMulinputs-input_784_to_32/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&input_784_to_32/BiasAdd/ReadVariableOpReadVariableOp/input_784_to_32_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
input_784_to_32/BiasAddBiasAdd input_784_to_32/MatMul:product:0.input_784_to_32/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
input_784_to_32/ReluRelu input_784_to_32/BiasAdd:output:0*
T0*'
_output_shapes
:          Ф
%hidden_linear_1/MatMul/ReadVariableOpReadVariableOp.hidden_linear_1_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0е
hidden_linear_1/MatMulMatMul"input_784_to_32/Relu:activations:0-hidden_linear_1/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&hidden_linear_1/BiasAdd/ReadVariableOpReadVariableOp/hidden_linear_1_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
hidden_linear_1/BiasAddBiasAdd hidden_linear_1/MatMul:product:0.hidden_linear_1/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
hidden_linear_1/ReluRelu hidden_linear_1/BiasAdd:output:0*
T0*'
_output_shapes
:          Ф
%hidden_linear_2/MatMul/ReadVariableOpReadVariableOp.hidden_linear_2_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0е
hidden_linear_2/MatMulMatMul"hidden_linear_1/Relu:activations:0-hidden_linear_2/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&hidden_linear_2/BiasAdd/ReadVariableOpReadVariableOp/hidden_linear_2_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
hidden_linear_2/BiasAddBiasAdd hidden_linear_2/MatMul:product:0.hidden_linear_2/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
hidden_linear_2/ReluRelu hidden_linear_2/BiasAdd:output:0*
T0*'
_output_shapes
:          Ф
%hidden_linear_3/MatMul/ReadVariableOpReadVariableOp.hidden_linear_3_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0е
hidden_linear_3/MatMulMatMul"hidden_linear_2/Relu:activations:0-hidden_linear_3/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Т
&hidden_linear_3/BiasAdd/ReadVariableOpReadVariableOp/hidden_linear_3_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0ж
hidden_linear_3/BiasAddBiasAdd hidden_linear_3/MatMul:product:0.hidden_linear_3/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          p
hidden_linear_3/ReluRelu hidden_linear_3/BiasAdd:output:0*
T0*'
_output_shapes
:          А
Dense/MatMul/ReadVariableOpReadVariableOp$dense_matmul_readvariableop_resource*
_output_shapes

: 
*
dtype0С
Dense/MatMulMatMul"hidden_linear_3/Relu:activations:0#Dense/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
~
Dense/BiasAdd/ReadVariableOpReadVariableOp%dense_biasadd_readvariableop_resource*
_output_shapes
:
*
dtype0И
Dense/BiasAddBiasAddDense/MatMul:product:0$Dense/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
e
IdentityIdentityDense/BiasAdd:output:0^NoOp*
T0*'
_output_shapes
:         
╟
NoOpNoOp^Dense/BiasAdd/ReadVariableOp^Dense/MatMul/ReadVariableOp'^hidden_linear_1/BiasAdd/ReadVariableOp&^hidden_linear_1/MatMul/ReadVariableOp'^hidden_linear_2/BiasAdd/ReadVariableOp&^hidden_linear_2/MatMul/ReadVariableOp'^hidden_linear_3/BiasAdd/ReadVariableOp&^hidden_linear_3/MatMul/ReadVariableOp'^input_784_to_32/BiasAdd/ReadVariableOp&^input_784_to_32/MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2<
Dense/BiasAdd/ReadVariableOpDense/BiasAdd/ReadVariableOp2:
Dense/MatMul/ReadVariableOpDense/MatMul/ReadVariableOp2P
&hidden_linear_1/BiasAdd/ReadVariableOp&hidden_linear_1/BiasAdd/ReadVariableOp2N
%hidden_linear_1/MatMul/ReadVariableOp%hidden_linear_1/MatMul/ReadVariableOp2P
&hidden_linear_2/BiasAdd/ReadVariableOp&hidden_linear_2/BiasAdd/ReadVariableOp2N
%hidden_linear_2/MatMul/ReadVariableOp%hidden_linear_2/MatMul/ReadVariableOp2P
&hidden_linear_3/BiasAdd/ReadVariableOp&hidden_linear_3/BiasAdd/ReadVariableOp2N
%hidden_linear_3/MatMul/ReadVariableOp%hidden_linear_3/MatMul/ReadVariableOp2P
&input_784_to_32/BiasAdd/ReadVariableOp&input_784_to_32/BiasAdd/ReadVariableOp2N
%input_784_to_32/MatMul/ReadVariableOp%input_784_to_32/MatMul/ReadVariableOp:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
б

√
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_40928

inputs0
matmul_readvariableop_resource:  -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:  *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
ё	
ъ
#__inference_signature_wrapper_41253
input_1
unknown:	Р 
	unknown_0: 
	unknown_1:  
	unknown_2: 
	unknown_3:  
	unknown_4: 
	unknown_5:  
	unknown_6: 
	unknown_7: 

	unknown_8:

identityИвStatefulPartitionedCallб
StatefulPartitionedCallStatefulPartitionedCallinput_1unknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*,
_read_only_resource_inputs

	
*0
config_proto 

CPU

GPU2*0J 8В *)
f$R"
 __inference__wrapped_model_40893o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:Q M
(
_output_shapes
:         Р
!
_user_specified_name	input_1
├	
ё
@__inference_Dense_layer_call_and_return_conditional_losses_40978

inputs0
matmul_readvariableop_resource: 
-
biasadd_readvariableop_resource:

identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

: 
*
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:
*
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
_
IdentityIdentityBiasAdd:output:0^NoOp*
T0*'
_output_shapes
:         
w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
Ъ

Ё
*__inference_sequential_layer_call_fn_41278

inputs
unknown:	Р 
	unknown_0: 
	unknown_1:  
	unknown_2: 
	unknown_3:  
	unknown_4: 
	unknown_5:  
	unknown_6: 
	unknown_7: 

	unknown_8:

identityИвStatefulPartitionedCall┼
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*,
_read_only_resource_inputs

	
*0
config_proto 

CPU

GPU2*0J 8В *N
fIRG
E__inference_sequential_layer_call_and_return_conditional_losses_40985o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
╤
Ь
/__inference_hidden_linear_1_layer_call_fn_41408

inputs
unknown:  
	unknown_0: 
identityИвStatefulPartitionedCallт
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_40928o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:          `
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
е

№
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_41399

inputs1
matmul_readvariableop_resource:	Р -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpu
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes
:	Р *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*+
_input_shapes
:         Р: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
б

√
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_41419

inputs0
matmul_readvariableop_resource:  -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:  *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
б

√
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_41459

inputs0
matmul_readvariableop_resource:  -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:  *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
б

√
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_40945

inputs0
matmul_readvariableop_resource:  -
biasadd_readvariableop_resource: 
identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:  *
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
: *
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:          a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:          w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
▌
Я
E__inference_sequential_layer_call_and_return_conditional_losses_41114

inputs(
input_784_to_32_41088:	Р #
input_784_to_32_41090: '
hidden_linear_1_41093:  #
hidden_linear_1_41095: '
hidden_linear_2_41098:  #
hidden_linear_2_41100: '
hidden_linear_3_41103:  #
hidden_linear_3_41105: 
dense_41108: 

dense_41110:

identityИвDense/StatefulPartitionedCallв'hidden_linear_1/StatefulPartitionedCallв'hidden_linear_2/StatefulPartitionedCallв'hidden_linear_3/StatefulPartitionedCallв'input_784_to_32/StatefulPartitionedCallМ
'input_784_to_32/StatefulPartitionedCallStatefulPartitionedCallinputsinput_784_to_32_41088input_784_to_32_41090*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_40911╢
'hidden_linear_1/StatefulPartitionedCallStatefulPartitionedCall0input_784_to_32/StatefulPartitionedCall:output:0hidden_linear_1_41093hidden_linear_1_41095*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_40928╢
'hidden_linear_2/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_1/StatefulPartitionedCall:output:0hidden_linear_2_41098hidden_linear_2_41100*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_40945╢
'hidden_linear_3/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_2/StatefulPartitionedCall:output:0hidden_linear_3_41103hidden_linear_3_41105*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_40962О
Dense/StatefulPartitionedCallStatefulPartitionedCall0hidden_linear_3/StatefulPartitionedCall:output:0dense_41108dense_41110*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *I
fDRB
@__inference_Dense_layer_call_and_return_conditional_losses_40978u
IdentityIdentity&Dense/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
О
NoOpNoOp^Dense/StatefulPartitionedCall(^hidden_linear_1/StatefulPartitionedCall(^hidden_linear_2/StatefulPartitionedCall(^hidden_linear_3/StatefulPartitionedCall(^input_784_to_32/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2>
Dense/StatefulPartitionedCallDense/StatefulPartitionedCall2R
'hidden_linear_1/StatefulPartitionedCall'hidden_linear_1/StatefulPartitionedCall2R
'hidden_linear_2/StatefulPartitionedCall'hidden_linear_2/StatefulPartitionedCall2R
'hidden_linear_3/StatefulPartitionedCall'hidden_linear_3/StatefulPartitionedCall2R
'input_784_to_32/StatefulPartitionedCall'input_784_to_32/StatefulPartitionedCall:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
╤
Ь
/__inference_hidden_linear_3_layer_call_fn_41448

inputs
unknown:  
	unknown_0: 
identityИвStatefulPartitionedCallт
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_40962o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:          `
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
Ъ

Ё
*__inference_sequential_layer_call_fn_41303

inputs
unknown:	Р 
	unknown_0: 
	unknown_1:  
	unknown_2: 
	unknown_3:  
	unknown_4: 
	unknown_5:  
	unknown_6: 
	unknown_7: 

	unknown_8:

identityИвStatefulPartitionedCall┼
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*,
_read_only_resource_inputs

	
*0
config_proto 

CPU

GPU2*0J 8В *N
fIRG
E__inference_sequential_layer_call_and_return_conditional_losses_41114o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
їЭ
║
!__inference__traced_restore_41745
file_prefix:
'assignvariableop_input_784_to_32_kernel:	Р 5
'assignvariableop_1_input_784_to_32_bias: ;
)assignvariableop_2_hidden_linear_1_kernel:  5
'assignvariableop_3_hidden_linear_1_bias: ;
)assignvariableop_4_hidden_linear_2_kernel:  5
'assignvariableop_5_hidden_linear_2_bias: ;
)assignvariableop_6_hidden_linear_3_kernel:  5
'assignvariableop_7_hidden_linear_3_bias: 1
assignvariableop_8_dense_kernel: 
+
assignvariableop_9_dense_bias:
'
assignvariableop_10_adam_iter:	 )
assignvariableop_11_adam_beta_1: )
assignvariableop_12_adam_beta_2: (
assignvariableop_13_adam_decay: 0
&assignvariableop_14_adam_learning_rate: #
assignvariableop_15_total: #
assignvariableop_16_count: %
assignvariableop_17_total_1: %
assignvariableop_18_count_1: D
1assignvariableop_19_adam_input_784_to_32_kernel_m:	Р =
/assignvariableop_20_adam_input_784_to_32_bias_m: C
1assignvariableop_21_adam_hidden_linear_1_kernel_m:  =
/assignvariableop_22_adam_hidden_linear_1_bias_m: C
1assignvariableop_23_adam_hidden_linear_2_kernel_m:  =
/assignvariableop_24_adam_hidden_linear_2_bias_m: C
1assignvariableop_25_adam_hidden_linear_3_kernel_m:  =
/assignvariableop_26_adam_hidden_linear_3_bias_m: 9
'assignvariableop_27_adam_dense_kernel_m: 
3
%assignvariableop_28_adam_dense_bias_m:
D
1assignvariableop_29_adam_input_784_to_32_kernel_v:	Р =
/assignvariableop_30_adam_input_784_to_32_bias_v: C
1assignvariableop_31_adam_hidden_linear_1_kernel_v:  =
/assignvariableop_32_adam_hidden_linear_1_bias_v: C
1assignvariableop_33_adam_hidden_linear_2_kernel_v:  =
/assignvariableop_34_adam_hidden_linear_2_bias_v: C
1assignvariableop_35_adam_hidden_linear_3_kernel_v:  =
/assignvariableop_36_adam_hidden_linear_3_bias_v: 9
'assignvariableop_37_adam_dense_kernel_v: 
3
%assignvariableop_38_adam_dense_bias_v:

identity_40ИвAssignVariableOpвAssignVariableOp_1вAssignVariableOp_10вAssignVariableOp_11вAssignVariableOp_12вAssignVariableOp_13вAssignVariableOp_14вAssignVariableOp_15вAssignVariableOp_16вAssignVariableOp_17вAssignVariableOp_18вAssignVariableOp_19вAssignVariableOp_2вAssignVariableOp_20вAssignVariableOp_21вAssignVariableOp_22вAssignVariableOp_23вAssignVariableOp_24вAssignVariableOp_25вAssignVariableOp_26вAssignVariableOp_27вAssignVariableOp_28вAssignVariableOp_29вAssignVariableOp_3вAssignVariableOp_30вAssignVariableOp_31вAssignVariableOp_32вAssignVariableOp_33вAssignVariableOp_34вAssignVariableOp_35вAssignVariableOp_36вAssignVariableOp_37вAssignVariableOp_38вAssignVariableOp_4вAssignVariableOp_5вAssignVariableOp_6вAssignVariableOp_7вAssignVariableOp_8вAssignVariableOp_9ь
RestoreV2/tensor_namesConst"/device:CPU:0*
_output_shapes
:(*
dtype0*Т
valueИBЕ(B6layer_with_weights-0/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-0/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-1/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-1/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-2/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-2/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-3/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-3/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-4/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-4/bias/.ATTRIBUTES/VARIABLE_VALUEB)optimizer/iter/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_1/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_2/.ATTRIBUTES/VARIABLE_VALUEB*optimizer/decay/.ATTRIBUTES/VARIABLE_VALUEB2optimizer/learning_rate/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/count/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/count/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-0/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-0/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-1/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-1/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-4/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-4/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-0/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-0/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-1/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-1/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-4/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-4/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEB_CHECKPOINTABLE_OBJECT_GRAPH└
RestoreV2/shape_and_slicesConst"/device:CPU:0*
_output_shapes
:(*
dtype0*c
valueZBX(B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B щ
	RestoreV2	RestoreV2file_prefixRestoreV2/tensor_names:output:0#RestoreV2/shape_and_slices:output:0"/device:CPU:0*╢
_output_shapesг
а::::::::::::::::::::::::::::::::::::::::*6
dtypes,
*2(	[
IdentityIdentityRestoreV2:tensors:0"/device:CPU:0*
T0*
_output_shapes
:Т
AssignVariableOpAssignVariableOp'assignvariableop_input_784_to_32_kernelIdentity:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_1IdentityRestoreV2:tensors:1"/device:CPU:0*
T0*
_output_shapes
:Ц
AssignVariableOp_1AssignVariableOp'assignvariableop_1_input_784_to_32_biasIdentity_1:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_2IdentityRestoreV2:tensors:2"/device:CPU:0*
T0*
_output_shapes
:Ш
AssignVariableOp_2AssignVariableOp)assignvariableop_2_hidden_linear_1_kernelIdentity_2:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_3IdentityRestoreV2:tensors:3"/device:CPU:0*
T0*
_output_shapes
:Ц
AssignVariableOp_3AssignVariableOp'assignvariableop_3_hidden_linear_1_biasIdentity_3:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_4IdentityRestoreV2:tensors:4"/device:CPU:0*
T0*
_output_shapes
:Ш
AssignVariableOp_4AssignVariableOp)assignvariableop_4_hidden_linear_2_kernelIdentity_4:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_5IdentityRestoreV2:tensors:5"/device:CPU:0*
T0*
_output_shapes
:Ц
AssignVariableOp_5AssignVariableOp'assignvariableop_5_hidden_linear_2_biasIdentity_5:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_6IdentityRestoreV2:tensors:6"/device:CPU:0*
T0*
_output_shapes
:Ш
AssignVariableOp_6AssignVariableOp)assignvariableop_6_hidden_linear_3_kernelIdentity_6:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_7IdentityRestoreV2:tensors:7"/device:CPU:0*
T0*
_output_shapes
:Ц
AssignVariableOp_7AssignVariableOp'assignvariableop_7_hidden_linear_3_biasIdentity_7:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_8IdentityRestoreV2:tensors:8"/device:CPU:0*
T0*
_output_shapes
:О
AssignVariableOp_8AssignVariableOpassignvariableop_8_dense_kernelIdentity_8:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_9IdentityRestoreV2:tensors:9"/device:CPU:0*
T0*
_output_shapes
:М
AssignVariableOp_9AssignVariableOpassignvariableop_9_dense_biasIdentity_9:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_10IdentityRestoreV2:tensors:10"/device:CPU:0*
T0	*
_output_shapes
:О
AssignVariableOp_10AssignVariableOpassignvariableop_10_adam_iterIdentity_10:output:0"/device:CPU:0*
_output_shapes
 *
dtype0	_
Identity_11IdentityRestoreV2:tensors:11"/device:CPU:0*
T0*
_output_shapes
:Р
AssignVariableOp_11AssignVariableOpassignvariableop_11_adam_beta_1Identity_11:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_12IdentityRestoreV2:tensors:12"/device:CPU:0*
T0*
_output_shapes
:Р
AssignVariableOp_12AssignVariableOpassignvariableop_12_adam_beta_2Identity_12:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_13IdentityRestoreV2:tensors:13"/device:CPU:0*
T0*
_output_shapes
:П
AssignVariableOp_13AssignVariableOpassignvariableop_13_adam_decayIdentity_13:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_14IdentityRestoreV2:tensors:14"/device:CPU:0*
T0*
_output_shapes
:Ч
AssignVariableOp_14AssignVariableOp&assignvariableop_14_adam_learning_rateIdentity_14:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_15IdentityRestoreV2:tensors:15"/device:CPU:0*
T0*
_output_shapes
:К
AssignVariableOp_15AssignVariableOpassignvariableop_15_totalIdentity_15:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_16IdentityRestoreV2:tensors:16"/device:CPU:0*
T0*
_output_shapes
:К
AssignVariableOp_16AssignVariableOpassignvariableop_16_countIdentity_16:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_17IdentityRestoreV2:tensors:17"/device:CPU:0*
T0*
_output_shapes
:М
AssignVariableOp_17AssignVariableOpassignvariableop_17_total_1Identity_17:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_18IdentityRestoreV2:tensors:18"/device:CPU:0*
T0*
_output_shapes
:М
AssignVariableOp_18AssignVariableOpassignvariableop_18_count_1Identity_18:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_19IdentityRestoreV2:tensors:19"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_19AssignVariableOp1assignvariableop_19_adam_input_784_to_32_kernel_mIdentity_19:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_20IdentityRestoreV2:tensors:20"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_20AssignVariableOp/assignvariableop_20_adam_input_784_to_32_bias_mIdentity_20:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_21IdentityRestoreV2:tensors:21"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_21AssignVariableOp1assignvariableop_21_adam_hidden_linear_1_kernel_mIdentity_21:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_22IdentityRestoreV2:tensors:22"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_22AssignVariableOp/assignvariableop_22_adam_hidden_linear_1_bias_mIdentity_22:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_23IdentityRestoreV2:tensors:23"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_23AssignVariableOp1assignvariableop_23_adam_hidden_linear_2_kernel_mIdentity_23:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_24IdentityRestoreV2:tensors:24"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_24AssignVariableOp/assignvariableop_24_adam_hidden_linear_2_bias_mIdentity_24:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_25IdentityRestoreV2:tensors:25"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_25AssignVariableOp1assignvariableop_25_adam_hidden_linear_3_kernel_mIdentity_25:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_26IdentityRestoreV2:tensors:26"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_26AssignVariableOp/assignvariableop_26_adam_hidden_linear_3_bias_mIdentity_26:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_27IdentityRestoreV2:tensors:27"/device:CPU:0*
T0*
_output_shapes
:Ш
AssignVariableOp_27AssignVariableOp'assignvariableop_27_adam_dense_kernel_mIdentity_27:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_28IdentityRestoreV2:tensors:28"/device:CPU:0*
T0*
_output_shapes
:Ц
AssignVariableOp_28AssignVariableOp%assignvariableop_28_adam_dense_bias_mIdentity_28:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_29IdentityRestoreV2:tensors:29"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_29AssignVariableOp1assignvariableop_29_adam_input_784_to_32_kernel_vIdentity_29:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_30IdentityRestoreV2:tensors:30"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_30AssignVariableOp/assignvariableop_30_adam_input_784_to_32_bias_vIdentity_30:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_31IdentityRestoreV2:tensors:31"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_31AssignVariableOp1assignvariableop_31_adam_hidden_linear_1_kernel_vIdentity_31:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_32IdentityRestoreV2:tensors:32"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_32AssignVariableOp/assignvariableop_32_adam_hidden_linear_1_bias_vIdentity_32:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_33IdentityRestoreV2:tensors:33"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_33AssignVariableOp1assignvariableop_33_adam_hidden_linear_2_kernel_vIdentity_33:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_34IdentityRestoreV2:tensors:34"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_34AssignVariableOp/assignvariableop_34_adam_hidden_linear_2_bias_vIdentity_34:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_35IdentityRestoreV2:tensors:35"/device:CPU:0*
T0*
_output_shapes
:в
AssignVariableOp_35AssignVariableOp1assignvariableop_35_adam_hidden_linear_3_kernel_vIdentity_35:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_36IdentityRestoreV2:tensors:36"/device:CPU:0*
T0*
_output_shapes
:а
AssignVariableOp_36AssignVariableOp/assignvariableop_36_adam_hidden_linear_3_bias_vIdentity_36:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_37IdentityRestoreV2:tensors:37"/device:CPU:0*
T0*
_output_shapes
:Ш
AssignVariableOp_37AssignVariableOp'assignvariableop_37_adam_dense_kernel_vIdentity_37:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_38IdentityRestoreV2:tensors:38"/device:CPU:0*
T0*
_output_shapes
:Ц
AssignVariableOp_38AssignVariableOp%assignvariableop_38_adam_dense_bias_vIdentity_38:output:0"/device:CPU:0*
_output_shapes
 *
dtype01
NoOpNoOp"/device:CPU:0*
_output_shapes
 й
Identity_39Identityfile_prefix^AssignVariableOp^AssignVariableOp_1^AssignVariableOp_10^AssignVariableOp_11^AssignVariableOp_12^AssignVariableOp_13^AssignVariableOp_14^AssignVariableOp_15^AssignVariableOp_16^AssignVariableOp_17^AssignVariableOp_18^AssignVariableOp_19^AssignVariableOp_2^AssignVariableOp_20^AssignVariableOp_21^AssignVariableOp_22^AssignVariableOp_23^AssignVariableOp_24^AssignVariableOp_25^AssignVariableOp_26^AssignVariableOp_27^AssignVariableOp_28^AssignVariableOp_29^AssignVariableOp_3^AssignVariableOp_30^AssignVariableOp_31^AssignVariableOp_32^AssignVariableOp_33^AssignVariableOp_34^AssignVariableOp_35^AssignVariableOp_36^AssignVariableOp_37^AssignVariableOp_38^AssignVariableOp_4^AssignVariableOp_5^AssignVariableOp_6^AssignVariableOp_7^AssignVariableOp_8^AssignVariableOp_9^NoOp"/device:CPU:0*
T0*
_output_shapes
: W
Identity_40IdentityIdentity_39:output:0^NoOp_1*
T0*
_output_shapes
: Ц
NoOp_1NoOp^AssignVariableOp^AssignVariableOp_1^AssignVariableOp_10^AssignVariableOp_11^AssignVariableOp_12^AssignVariableOp_13^AssignVariableOp_14^AssignVariableOp_15^AssignVariableOp_16^AssignVariableOp_17^AssignVariableOp_18^AssignVariableOp_19^AssignVariableOp_2^AssignVariableOp_20^AssignVariableOp_21^AssignVariableOp_22^AssignVariableOp_23^AssignVariableOp_24^AssignVariableOp_25^AssignVariableOp_26^AssignVariableOp_27^AssignVariableOp_28^AssignVariableOp_29^AssignVariableOp_3^AssignVariableOp_30^AssignVariableOp_31^AssignVariableOp_32^AssignVariableOp_33^AssignVariableOp_34^AssignVariableOp_35^AssignVariableOp_36^AssignVariableOp_37^AssignVariableOp_38^AssignVariableOp_4^AssignVariableOp_5^AssignVariableOp_6^AssignVariableOp_7^AssignVariableOp_8^AssignVariableOp_9*"
_acd_function_control_output(*
_output_shapes
 "#
identity_40Identity_40:output:0*c
_input_shapesR
P: : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 2$
AssignVariableOpAssignVariableOp2(
AssignVariableOp_1AssignVariableOp_12*
AssignVariableOp_10AssignVariableOp_102*
AssignVariableOp_11AssignVariableOp_112*
AssignVariableOp_12AssignVariableOp_122*
AssignVariableOp_13AssignVariableOp_132*
AssignVariableOp_14AssignVariableOp_142*
AssignVariableOp_15AssignVariableOp_152*
AssignVariableOp_16AssignVariableOp_162*
AssignVariableOp_17AssignVariableOp_172*
AssignVariableOp_18AssignVariableOp_182*
AssignVariableOp_19AssignVariableOp_192(
AssignVariableOp_2AssignVariableOp_22*
AssignVariableOp_20AssignVariableOp_202*
AssignVariableOp_21AssignVariableOp_212*
AssignVariableOp_22AssignVariableOp_222*
AssignVariableOp_23AssignVariableOp_232*
AssignVariableOp_24AssignVariableOp_242*
AssignVariableOp_25AssignVariableOp_252*
AssignVariableOp_26AssignVariableOp_262*
AssignVariableOp_27AssignVariableOp_272*
AssignVariableOp_28AssignVariableOp_282*
AssignVariableOp_29AssignVariableOp_292(
AssignVariableOp_3AssignVariableOp_32*
AssignVariableOp_30AssignVariableOp_302*
AssignVariableOp_31AssignVariableOp_312*
AssignVariableOp_32AssignVariableOp_322*
AssignVariableOp_33AssignVariableOp_332*
AssignVariableOp_34AssignVariableOp_342*
AssignVariableOp_35AssignVariableOp_352*
AssignVariableOp_36AssignVariableOp_362*
AssignVariableOp_37AssignVariableOp_372*
AssignVariableOp_38AssignVariableOp_382(
AssignVariableOp_4AssignVariableOp_42(
AssignVariableOp_5AssignVariableOp_52(
AssignVariableOp_6AssignVariableOp_62(
AssignVariableOp_7AssignVariableOp_72(
AssignVariableOp_8AssignVariableOp_82(
AssignVariableOp_9AssignVariableOp_9:C ?

_output_shapes
: 
%
_user_specified_namefile_prefix
╜
Т
%__inference_Dense_layer_call_fn_41468

inputs
unknown: 

	unknown_0:

identityИвStatefulPartitionedCall╪
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *I
fDRB
@__inference_Dense_layer_call_and_return_conditional_losses_40978o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
├	
ё
@__inference_Dense_layer_call_and_return_conditional_losses_41478

inputs0
matmul_readvariableop_resource: 
-
biasadd_readvariableop_resource:

identityИвBiasAdd/ReadVariableOpвMatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

: 
*
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:
*
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
_
IdentityIdentityBiasAdd:output:0^NoOp*
T0*'
_output_shapes
:         
w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:          : : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:          
 
_user_specified_nameinputs
█R
Л
__inference__traced_save_41618
file_prefix5
1savev2_input_784_to_32_kernel_read_readvariableop3
/savev2_input_784_to_32_bias_read_readvariableop5
1savev2_hidden_linear_1_kernel_read_readvariableop3
/savev2_hidden_linear_1_bias_read_readvariableop5
1savev2_hidden_linear_2_kernel_read_readvariableop3
/savev2_hidden_linear_2_bias_read_readvariableop5
1savev2_hidden_linear_3_kernel_read_readvariableop3
/savev2_hidden_linear_3_bias_read_readvariableop+
'savev2_dense_kernel_read_readvariableop)
%savev2_dense_bias_read_readvariableop(
$savev2_adam_iter_read_readvariableop	*
&savev2_adam_beta_1_read_readvariableop*
&savev2_adam_beta_2_read_readvariableop)
%savev2_adam_decay_read_readvariableop1
-savev2_adam_learning_rate_read_readvariableop$
 savev2_total_read_readvariableop$
 savev2_count_read_readvariableop&
"savev2_total_1_read_readvariableop&
"savev2_count_1_read_readvariableop<
8savev2_adam_input_784_to_32_kernel_m_read_readvariableop:
6savev2_adam_input_784_to_32_bias_m_read_readvariableop<
8savev2_adam_hidden_linear_1_kernel_m_read_readvariableop:
6savev2_adam_hidden_linear_1_bias_m_read_readvariableop<
8savev2_adam_hidden_linear_2_kernel_m_read_readvariableop:
6savev2_adam_hidden_linear_2_bias_m_read_readvariableop<
8savev2_adam_hidden_linear_3_kernel_m_read_readvariableop:
6savev2_adam_hidden_linear_3_bias_m_read_readvariableop2
.savev2_adam_dense_kernel_m_read_readvariableop0
,savev2_adam_dense_bias_m_read_readvariableop<
8savev2_adam_input_784_to_32_kernel_v_read_readvariableop:
6savev2_adam_input_784_to_32_bias_v_read_readvariableop<
8savev2_adam_hidden_linear_1_kernel_v_read_readvariableop:
6savev2_adam_hidden_linear_1_bias_v_read_readvariableop<
8savev2_adam_hidden_linear_2_kernel_v_read_readvariableop:
6savev2_adam_hidden_linear_2_bias_v_read_readvariableop<
8savev2_adam_hidden_linear_3_kernel_v_read_readvariableop:
6savev2_adam_hidden_linear_3_bias_v_read_readvariableop2
.savev2_adam_dense_kernel_v_read_readvariableop0
,savev2_adam_dense_bias_v_read_readvariableop
savev2_const

identity_1ИвMergeV2Checkpointsw
StaticRegexFullMatchStaticRegexFullMatchfile_prefix"/device:CPU:**
_output_shapes
: *
pattern
^s3://.*Z
ConstConst"/device:CPU:**
_output_shapes
: *
dtype0*
valueB B.parta
Const_1Const"/device:CPU:**
_output_shapes
: *
dtype0*
valueB B
_temp/partБ
SelectSelectStaticRegexFullMatch:output:0Const:output:0Const_1:output:0"/device:CPU:**
T0*
_output_shapes
: f

StringJoin
StringJoinfile_prefixSelect:output:0"/device:CPU:**
N*
_output_shapes
: L

num_shardsConst*
_output_shapes
: *
dtype0*
value	B :f
ShardedFilename/shardConst"/device:CPU:0*
_output_shapes
: *
dtype0*
value	B : У
ShardedFilenameShardedFilenameStringJoin:output:0ShardedFilename/shard:output:0num_shards:output:0"/device:CPU:0*
_output_shapes
: щ
SaveV2/tensor_namesConst"/device:CPU:0*
_output_shapes
:(*
dtype0*Т
valueИBЕ(B6layer_with_weights-0/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-0/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-1/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-1/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-2/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-2/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-3/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-3/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-4/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-4/bias/.ATTRIBUTES/VARIABLE_VALUEB)optimizer/iter/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_1/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_2/.ATTRIBUTES/VARIABLE_VALUEB*optimizer/decay/.ATTRIBUTES/VARIABLE_VALUEB2optimizer/learning_rate/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/count/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/count/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-0/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-0/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-1/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-1/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-4/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-4/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-0/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-0/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-1/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-1/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-4/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-4/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEB_CHECKPOINTABLE_OBJECT_GRAPH╜
SaveV2/shape_and_slicesConst"/device:CPU:0*
_output_shapes
:(*
dtype0*c
valueZBX(B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B █
SaveV2SaveV2ShardedFilename:filename:0SaveV2/tensor_names:output:0 SaveV2/shape_and_slices:output:01savev2_input_784_to_32_kernel_read_readvariableop/savev2_input_784_to_32_bias_read_readvariableop1savev2_hidden_linear_1_kernel_read_readvariableop/savev2_hidden_linear_1_bias_read_readvariableop1savev2_hidden_linear_2_kernel_read_readvariableop/savev2_hidden_linear_2_bias_read_readvariableop1savev2_hidden_linear_3_kernel_read_readvariableop/savev2_hidden_linear_3_bias_read_readvariableop'savev2_dense_kernel_read_readvariableop%savev2_dense_bias_read_readvariableop$savev2_adam_iter_read_readvariableop&savev2_adam_beta_1_read_readvariableop&savev2_adam_beta_2_read_readvariableop%savev2_adam_decay_read_readvariableop-savev2_adam_learning_rate_read_readvariableop savev2_total_read_readvariableop savev2_count_read_readvariableop"savev2_total_1_read_readvariableop"savev2_count_1_read_readvariableop8savev2_adam_input_784_to_32_kernel_m_read_readvariableop6savev2_adam_input_784_to_32_bias_m_read_readvariableop8savev2_adam_hidden_linear_1_kernel_m_read_readvariableop6savev2_adam_hidden_linear_1_bias_m_read_readvariableop8savev2_adam_hidden_linear_2_kernel_m_read_readvariableop6savev2_adam_hidden_linear_2_bias_m_read_readvariableop8savev2_adam_hidden_linear_3_kernel_m_read_readvariableop6savev2_adam_hidden_linear_3_bias_m_read_readvariableop.savev2_adam_dense_kernel_m_read_readvariableop,savev2_adam_dense_bias_m_read_readvariableop8savev2_adam_input_784_to_32_kernel_v_read_readvariableop6savev2_adam_input_784_to_32_bias_v_read_readvariableop8savev2_adam_hidden_linear_1_kernel_v_read_readvariableop6savev2_adam_hidden_linear_1_bias_v_read_readvariableop8savev2_adam_hidden_linear_2_kernel_v_read_readvariableop6savev2_adam_hidden_linear_2_bias_v_read_readvariableop8savev2_adam_hidden_linear_3_kernel_v_read_readvariableop6savev2_adam_hidden_linear_3_bias_v_read_readvariableop.savev2_adam_dense_kernel_v_read_readvariableop,savev2_adam_dense_bias_v_read_readvariableopsavev2_const"/device:CPU:0*
_output_shapes
 *6
dtypes,
*2(	Р
&MergeV2Checkpoints/checkpoint_prefixesPackShardedFilename:filename:0^SaveV2"/device:CPU:0*
N*
T0*
_output_shapes
:Л
MergeV2CheckpointsMergeV2Checkpoints/MergeV2Checkpoints/checkpoint_prefixes:output:0file_prefix"/device:CPU:0*
_output_shapes
 f
IdentityIdentityfile_prefix^MergeV2Checkpoints"/device:CPU:0*
T0*
_output_shapes
: Q

Identity_1IdentityIdentity:output:0^NoOp*
T0*
_output_shapes
: [
NoOpNoOp^MergeV2Checkpoints*"
_acd_function_control_output(*
_output_shapes
 "!

identity_1Identity_1:output:0*Ю
_input_shapesМ
Й: :	Р : :  : :  : :  : : 
:
: : : : : : : : : :	Р : :  : :  : :  : : 
:
:	Р : :  : :  : :  : : 
:
: 2(
MergeV2CheckpointsMergeV2Checkpoints:C ?

_output_shapes
: 
%
_user_specified_namefile_prefix:%!

_output_shapes
:	Р : 

_output_shapes
: :$ 

_output_shapes

:  : 

_output_shapes
: :$ 

_output_shapes

:  : 

_output_shapes
: :$ 

_output_shapes

:  : 

_output_shapes
: :$	 

_output_shapes

: 
: 


_output_shapes
:
:

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :%!

_output_shapes
:	Р : 

_output_shapes
: :$ 

_output_shapes

:  : 

_output_shapes
: :$ 

_output_shapes

:  : 

_output_shapes
: :$ 

_output_shapes

:  : 

_output_shapes
: :$ 

_output_shapes

: 
: 

_output_shapes
:
:%!

_output_shapes
:	Р : 

_output_shapes
: :$  

_output_shapes

:  : !

_output_shapes
: :$" 

_output_shapes

:  : #

_output_shapes
: :$$ 

_output_shapes

:  : %

_output_shapes
: :$& 

_output_shapes

: 
: '

_output_shapes
:
:(

_output_shapes
: 
╘
Э
/__inference_input_784_to_32_layer_call_fn_41388

inputs
unknown:	Р 
	unknown_0: 
identityИвStatefulPartitionedCallт
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:          *$
_read_only_resource_inputs
*0
config_proto 

CPU

GPU2*0J 8В *S
fNRL
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_40911o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:          `
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*+
_input_shapes
:         Р: : 22
StatefulPartitionedCallStatefulPartitionedCall:P L
(
_output_shapes
:         Р
 
_user_specified_nameinputs
Э

ё
*__inference_sequential_layer_call_fn_41162
input_1
unknown:	Р 
	unknown_0: 
	unknown_1:  
	unknown_2: 
	unknown_3:  
	unknown_4: 
	unknown_5:  
	unknown_6: 
	unknown_7: 

	unknown_8:

identityИвStatefulPartitionedCall╞
StatefulPartitionedCallStatefulPartitionedCallinput_1unknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:         
*,
_read_only_resource_inputs

	
*0
config_proto 

CPU

GPU2*0J 8В *N
fIRG
E__inference_sequential_layer_call_and_return_conditional_losses_41114o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:         
`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:Q M
(
_output_shapes
:         Р
!
_user_specified_name	input_1
п9
П

 __inference__wrapped_model_40893
input_1L
9sequential_input_784_to_32_matmul_readvariableop_resource:	Р H
:sequential_input_784_to_32_biasadd_readvariableop_resource: K
9sequential_hidden_linear_1_matmul_readvariableop_resource:  H
:sequential_hidden_linear_1_biasadd_readvariableop_resource: K
9sequential_hidden_linear_2_matmul_readvariableop_resource:  H
:sequential_hidden_linear_2_biasadd_readvariableop_resource: K
9sequential_hidden_linear_3_matmul_readvariableop_resource:  H
:sequential_hidden_linear_3_biasadd_readvariableop_resource: A
/sequential_dense_matmul_readvariableop_resource: 
>
0sequential_dense_biasadd_readvariableop_resource:

identityИв'sequential/Dense/BiasAdd/ReadVariableOpв&sequential/Dense/MatMul/ReadVariableOpв1sequential/hidden_linear_1/BiasAdd/ReadVariableOpв0sequential/hidden_linear_1/MatMul/ReadVariableOpв1sequential/hidden_linear_2/BiasAdd/ReadVariableOpв0sequential/hidden_linear_2/MatMul/ReadVariableOpв1sequential/hidden_linear_3/BiasAdd/ReadVariableOpв0sequential/hidden_linear_3/MatMul/ReadVariableOpв1sequential/input_784_to_32/BiasAdd/ReadVariableOpв0sequential/input_784_to_32/MatMul/ReadVariableOpл
0sequential/input_784_to_32/MatMul/ReadVariableOpReadVariableOp9sequential_input_784_to_32_matmul_readvariableop_resource*
_output_shapes
:	Р *
dtype0а
!sequential/input_784_to_32/MatMulMatMulinput_18sequential/input_784_to_32/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          и
1sequential/input_784_to_32/BiasAdd/ReadVariableOpReadVariableOp:sequential_input_784_to_32_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0╟
"sequential/input_784_to_32/BiasAddBiasAdd+sequential/input_784_to_32/MatMul:product:09sequential/input_784_to_32/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Ж
sequential/input_784_to_32/ReluRelu+sequential/input_784_to_32/BiasAdd:output:0*
T0*'
_output_shapes
:          к
0sequential/hidden_linear_1/MatMul/ReadVariableOpReadVariableOp9sequential_hidden_linear_1_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0╞
!sequential/hidden_linear_1/MatMulMatMul-sequential/input_784_to_32/Relu:activations:08sequential/hidden_linear_1/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          и
1sequential/hidden_linear_1/BiasAdd/ReadVariableOpReadVariableOp:sequential_hidden_linear_1_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0╟
"sequential/hidden_linear_1/BiasAddBiasAdd+sequential/hidden_linear_1/MatMul:product:09sequential/hidden_linear_1/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Ж
sequential/hidden_linear_1/ReluRelu+sequential/hidden_linear_1/BiasAdd:output:0*
T0*'
_output_shapes
:          к
0sequential/hidden_linear_2/MatMul/ReadVariableOpReadVariableOp9sequential_hidden_linear_2_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0╞
!sequential/hidden_linear_2/MatMulMatMul-sequential/hidden_linear_1/Relu:activations:08sequential/hidden_linear_2/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          и
1sequential/hidden_linear_2/BiasAdd/ReadVariableOpReadVariableOp:sequential_hidden_linear_2_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0╟
"sequential/hidden_linear_2/BiasAddBiasAdd+sequential/hidden_linear_2/MatMul:product:09sequential/hidden_linear_2/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Ж
sequential/hidden_linear_2/ReluRelu+sequential/hidden_linear_2/BiasAdd:output:0*
T0*'
_output_shapes
:          к
0sequential/hidden_linear_3/MatMul/ReadVariableOpReadVariableOp9sequential_hidden_linear_3_matmul_readvariableop_resource*
_output_shapes

:  *
dtype0╞
!sequential/hidden_linear_3/MatMulMatMul-sequential/hidden_linear_2/Relu:activations:08sequential/hidden_linear_3/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:          и
1sequential/hidden_linear_3/BiasAdd/ReadVariableOpReadVariableOp:sequential_hidden_linear_3_biasadd_readvariableop_resource*
_output_shapes
: *
dtype0╟
"sequential/hidden_linear_3/BiasAddBiasAdd+sequential/hidden_linear_3/MatMul:product:09sequential/hidden_linear_3/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:          Ж
sequential/hidden_linear_3/ReluRelu+sequential/hidden_linear_3/BiasAdd:output:0*
T0*'
_output_shapes
:          Ц
&sequential/Dense/MatMul/ReadVariableOpReadVariableOp/sequential_dense_matmul_readvariableop_resource*
_output_shapes

: 
*
dtype0▓
sequential/Dense/MatMulMatMul-sequential/hidden_linear_3/Relu:activations:0.sequential/Dense/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
Ф
'sequential/Dense/BiasAdd/ReadVariableOpReadVariableOp0sequential_dense_biasadd_readvariableop_resource*
_output_shapes
:
*
dtype0й
sequential/Dense/BiasAddBiasAdd!sequential/Dense/MatMul:product:0/sequential/Dense/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:         
p
IdentityIdentity!sequential/Dense/BiasAdd:output:0^NoOp*
T0*'
_output_shapes
:         
╡
NoOpNoOp(^sequential/Dense/BiasAdd/ReadVariableOp'^sequential/Dense/MatMul/ReadVariableOp2^sequential/hidden_linear_1/BiasAdd/ReadVariableOp1^sequential/hidden_linear_1/MatMul/ReadVariableOp2^sequential/hidden_linear_2/BiasAdd/ReadVariableOp1^sequential/hidden_linear_2/MatMul/ReadVariableOp2^sequential/hidden_linear_3/BiasAdd/ReadVariableOp1^sequential/hidden_linear_3/MatMul/ReadVariableOp2^sequential/input_784_to_32/BiasAdd/ReadVariableOp1^sequential/input_784_to_32/MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*;
_input_shapes*
(:         Р: : : : : : : : : : 2R
'sequential/Dense/BiasAdd/ReadVariableOp'sequential/Dense/BiasAdd/ReadVariableOp2P
&sequential/Dense/MatMul/ReadVariableOp&sequential/Dense/MatMul/ReadVariableOp2f
1sequential/hidden_linear_1/BiasAdd/ReadVariableOp1sequential/hidden_linear_1/BiasAdd/ReadVariableOp2d
0sequential/hidden_linear_1/MatMul/ReadVariableOp0sequential/hidden_linear_1/MatMul/ReadVariableOp2f
1sequential/hidden_linear_2/BiasAdd/ReadVariableOp1sequential/hidden_linear_2/BiasAdd/ReadVariableOp2d
0sequential/hidden_linear_2/MatMul/ReadVariableOp0sequential/hidden_linear_2/MatMul/ReadVariableOp2f
1sequential/hidden_linear_3/BiasAdd/ReadVariableOp1sequential/hidden_linear_3/BiasAdd/ReadVariableOp2d
0sequential/hidden_linear_3/MatMul/ReadVariableOp0sequential/hidden_linear_3/MatMul/ReadVariableOp2f
1sequential/input_784_to_32/BiasAdd/ReadVariableOp1sequential/input_784_to_32/BiasAdd/ReadVariableOp2d
0sequential/input_784_to_32/MatMul/ReadVariableOp0sequential/input_784_to_32/MatMul/ReadVariableOp:Q M
(
_output_shapes
:         Р
!
_user_specified_name	input_1"ВL
saver_filename:0StatefulPartitionedCall_1:0StatefulPartitionedCall_28"
saved_model_main_op

NoOp*>
__saved_model_init_op%#
__saved_model_init_op

NoOp*й
serving_defaultХ
<
input_11
serving_default_input_1:0         Р9
Dense0
StatefulPartitionedCall:0         
tensorflow/serving/predict:▀m
й
layer_with_weights-0
layer-0
layer_with_weights-1
layer-1
layer_with_weights-2
layer-2
layer_with_weights-3
layer-3
layer_with_weights-4
layer-4
	optimizer
	variables
trainable_variables
	regularization_losses

	keras_api

signatures
l__call__
*m&call_and_return_all_conditional_losses
n_default_save_signature"
_tf_keras_sequential
╗

kernel
bias
	variables
trainable_variables
regularization_losses
	keras_api
o__call__
*p&call_and_return_all_conditional_losses"
_tf_keras_layer
╗

kernel
bias
	variables
trainable_variables
regularization_losses
	keras_api
q__call__
*r&call_and_return_all_conditional_losses"
_tf_keras_layer
╗

kernel
bias
	variables
trainable_variables
regularization_losses
	keras_api
s__call__
*t&call_and_return_all_conditional_losses"
_tf_keras_layer
╗

kernel
bias
 	variables
!trainable_variables
"regularization_losses
#	keras_api
u__call__
*v&call_and_return_all_conditional_losses"
_tf_keras_layer
╗

$kernel
%bias
&	variables
'trainable_variables
(regularization_losses
)	keras_api
w__call__
*x&call_and_return_all_conditional_losses"
_tf_keras_layer
З
*iter

+beta_1

,beta_2
	-decay
.learning_ratemXmYmZm[m\m]m^m_$m`%mavbvcvdvevfvgvhvi$vj%vk"
	optimizer
f
0
1
2
3
4
5
6
7
$8
%9"
trackable_list_wrapper
f
0
1
2
3
4
5
6
7
$8
%9"
trackable_list_wrapper
 "
trackable_list_wrapper
╩
/non_trainable_variables

0layers
1metrics
2layer_regularization_losses
3layer_metrics
	variables
trainable_variables
	regularization_losses
l__call__
n_default_save_signature
*m&call_and_return_all_conditional_losses
&m"call_and_return_conditional_losses"
_generic_user_object
,
yserving_default"
signature_map
):'	Р 2input_784_to_32/kernel
":  2input_784_to_32/bias
.
0
1"
trackable_list_wrapper
.
0
1"
trackable_list_wrapper
 "
trackable_list_wrapper
н
4non_trainable_variables

5layers
6metrics
7layer_regularization_losses
8layer_metrics
	variables
trainable_variables
regularization_losses
o__call__
*p&call_and_return_all_conditional_losses
&p"call_and_return_conditional_losses"
_generic_user_object
(:&  2hidden_linear_1/kernel
":  2hidden_linear_1/bias
.
0
1"
trackable_list_wrapper
.
0
1"
trackable_list_wrapper
 "
trackable_list_wrapper
н
9non_trainable_variables

:layers
;metrics
<layer_regularization_losses
=layer_metrics
	variables
trainable_variables
regularization_losses
q__call__
*r&call_and_return_all_conditional_losses
&r"call_and_return_conditional_losses"
_generic_user_object
(:&  2hidden_linear_2/kernel
":  2hidden_linear_2/bias
.
0
1"
trackable_list_wrapper
.
0
1"
trackable_list_wrapper
 "
trackable_list_wrapper
н
>non_trainable_variables

?layers
@metrics
Alayer_regularization_losses
Blayer_metrics
	variables
trainable_variables
regularization_losses
s__call__
*t&call_and_return_all_conditional_losses
&t"call_and_return_conditional_losses"
_generic_user_object
(:&  2hidden_linear_3/kernel
":  2hidden_linear_3/bias
.
0
1"
trackable_list_wrapper
.
0
1"
trackable_list_wrapper
 "
trackable_list_wrapper
н
Cnon_trainable_variables

Dlayers
Emetrics
Flayer_regularization_losses
Glayer_metrics
 	variables
!trainable_variables
"regularization_losses
u__call__
*v&call_and_return_all_conditional_losses
&v"call_and_return_conditional_losses"
_generic_user_object
: 
2Dense/kernel
:
2
Dense/bias
.
$0
%1"
trackable_list_wrapper
.
$0
%1"
trackable_list_wrapper
 "
trackable_list_wrapper
н
Hnon_trainable_variables

Ilayers
Jmetrics
Klayer_regularization_losses
Llayer_metrics
&	variables
'trainable_variables
(regularization_losses
w__call__
*x&call_and_return_all_conditional_losses
&x"call_and_return_conditional_losses"
_generic_user_object
:	 (2	Adam/iter
: (2Adam/beta_1
: (2Adam/beta_2
: (2
Adam/decay
: (2Adam/learning_rate
 "
trackable_list_wrapper
C
0
1
2
3
4"
trackable_list_wrapper
.
M0
N1"
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
N
	Ototal
	Pcount
Q	variables
R	keras_api"
_tf_keras_metric
^
	Stotal
	Tcount
U
_fn_kwargs
V	variables
W	keras_api"
_tf_keras_metric
:  (2total
:  (2count
.
O0
P1"
trackable_list_wrapper
-
Q	variables"
_generic_user_object
:  (2total
:  (2count
 "
trackable_dict_wrapper
.
S0
T1"
trackable_list_wrapper
-
V	variables"
_generic_user_object
.:,	Р 2Adam/input_784_to_32/kernel/m
':% 2Adam/input_784_to_32/bias/m
-:+  2Adam/hidden_linear_1/kernel/m
':% 2Adam/hidden_linear_1/bias/m
-:+  2Adam/hidden_linear_2/kernel/m
':% 2Adam/hidden_linear_2/bias/m
-:+  2Adam/hidden_linear_3/kernel/m
':% 2Adam/hidden_linear_3/bias/m
#:! 
2Adam/Dense/kernel/m
:
2Adam/Dense/bias/m
.:,	Р 2Adam/input_784_to_32/kernel/v
':% 2Adam/input_784_to_32/bias/v
-:+  2Adam/hidden_linear_1/kernel/v
':% 2Adam/hidden_linear_1/bias/v
-:+  2Adam/hidden_linear_2/kernel/v
':% 2Adam/hidden_linear_2/bias/v
-:+  2Adam/hidden_linear_3/kernel/v
':% 2Adam/hidden_linear_3/bias/v
#:! 
2Adam/Dense/kernel/v
:
2Adam/Dense/bias/v
Ў2є
*__inference_sequential_layer_call_fn_41008
*__inference_sequential_layer_call_fn_41278
*__inference_sequential_layer_call_fn_41303
*__inference_sequential_layer_call_fn_41162└
╖▓│
FullArgSpec1
args)Ъ&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaultsЪ
p 

 

kwonlyargsЪ 
kwonlydefaultsк 
annotationsк *
 
т2▀
E__inference_sequential_layer_call_and_return_conditional_losses_41341
E__inference_sequential_layer_call_and_return_conditional_losses_41379
E__inference_sequential_layer_call_and_return_conditional_losses_41191
E__inference_sequential_layer_call_and_return_conditional_losses_41220└
╖▓│
FullArgSpec1
args)Ъ&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaultsЪ
p 

 

kwonlyargsЪ 
kwonlydefaultsк 
annotationsк *
 
╦B╚
 __inference__wrapped_model_40893input_1"Ш
С▓Н
FullArgSpec
argsЪ 
varargsjargs
varkwjkwargs
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
┘2╓
/__inference_input_784_to_32_layer_call_fn_41388в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
Ї2ё
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_41399в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
┘2╓
/__inference_hidden_linear_1_layer_call_fn_41408в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
Ї2ё
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_41419в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
┘2╓
/__inference_hidden_linear_2_layer_call_fn_41428в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
Ї2ё
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_41439в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
┘2╓
/__inference_hidden_linear_3_layer_call_fn_41448в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
Ї2ё
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_41459в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
╧2╠
%__inference_Dense_layer_call_fn_41468в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
ъ2ч
@__inference_Dense_layer_call_and_return_conditional_losses_41478в
Щ▓Х
FullArgSpec
argsЪ
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 
╩B╟
#__inference_signature_wrapper_41253input_1"Ф
Н▓Й
FullArgSpec
argsЪ 
varargs
 
varkwjkwargs
defaults
 

kwonlyargsЪ 
kwonlydefaults
 
annotationsк *
 а
@__inference_Dense_layer_call_and_return_conditional_losses_41478\$%/в,
%в"
 К
inputs          
к "%в"
К
0         

Ъ x
%__inference_Dense_layer_call_fn_41468O$%/в,
%в"
 К
inputs          
к "К         
Т
 __inference__wrapped_model_40893n
$%1в.
'в$
"К
input_1         Р
к "-к*
(
DenseК
Dense         
к
J__inference_hidden_linear_1_layer_call_and_return_conditional_losses_41419\/в,
%в"
 К
inputs          
к "%в"
К
0          
Ъ В
/__inference_hidden_linear_1_layer_call_fn_41408O/в,
%в"
 К
inputs          
к "К          к
J__inference_hidden_linear_2_layer_call_and_return_conditional_losses_41439\/в,
%в"
 К
inputs          
к "%в"
К
0          
Ъ В
/__inference_hidden_linear_2_layer_call_fn_41428O/в,
%в"
 К
inputs          
к "К          к
J__inference_hidden_linear_3_layer_call_and_return_conditional_losses_41459\/в,
%в"
 К
inputs          
к "%в"
К
0          
Ъ В
/__inference_hidden_linear_3_layer_call_fn_41448O/в,
%в"
 К
inputs          
к "К          л
J__inference_input_784_to_32_layer_call_and_return_conditional_losses_41399]0в-
&в#
!К
inputs         Р
к "%в"
К
0          
Ъ Г
/__inference_input_784_to_32_layer_call_fn_41388P0в-
&в#
!К
inputs         Р
к "К          ╖
E__inference_sequential_layer_call_and_return_conditional_losses_41191n
$%9в6
/в,
"К
input_1         Р
p 

 
к "%в"
К
0         

Ъ ╖
E__inference_sequential_layer_call_and_return_conditional_losses_41220n
$%9в6
/в,
"К
input_1         Р
p

 
к "%в"
К
0         

Ъ ╢
E__inference_sequential_layer_call_and_return_conditional_losses_41341m
$%8в5
.в+
!К
inputs         Р
p 

 
к "%в"
К
0         

Ъ ╢
E__inference_sequential_layer_call_and_return_conditional_losses_41379m
$%8в5
.в+
!К
inputs         Р
p

 
к "%в"
К
0         

Ъ П
*__inference_sequential_layer_call_fn_41008a
$%9в6
/в,
"К
input_1         Р
p 

 
к "К         
П
*__inference_sequential_layer_call_fn_41162a
$%9в6
/в,
"К
input_1         Р
p

 
к "К         
О
*__inference_sequential_layer_call_fn_41278`
$%8в5
.в+
!К
inputs         Р
p 

 
к "К         
О
*__inference_sequential_layer_call_fn_41303`
$%8в5
.в+
!К
inputs         Р
p

 
к "К         
а
#__inference_signature_wrapper_41253y
$%<в9
в 
2к/
-
input_1"К
input_1         Р"-к*
(
DenseК
Dense         
