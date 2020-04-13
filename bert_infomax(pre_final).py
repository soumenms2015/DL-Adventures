# -*- coding: utf-8 -*-
"""bert-infomax(pre-final).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/
"""

from google.colab import drive
drive.mount('/content/gdrive')

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow as tf

!pip install bert-tensorflow
import bert
from bert import run_classifier

from bert import optimization
from bert import tokenization

!wget https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip

!ls

!unzip multi_cased_L-12_H-768_A-12.zip

!ls

import pandas as pd
file = '/content/gdrive/My Drive/multilingual grounded/final.csv'
df = pd.read_csv(file)

from sklearn.model_selection import train_test_split

train, test = train_test_split(df, test_size=0.1,random_state = 42,shuffle = True)

def get_data_eng(a):
  b_ = list(a['gold_label'])
  lab = []
  """
  lab  = []
  for i in b_:
    lab.append(i-1)
  """
  for i in b_:
    if i=='contradiction':
        lab.append(0)
        
    elif i=='neutral':
        lab.append(1)
    elif i== 'entailment':
        lab.append(2)
    else:
        lab.append(3)
  sentence_1 = list(a['premise'])
  sentence_2 = list(a['hypo'])
  raw_data_train = {'sentence1_eng': sentence_1, 
              'sentence2_eng': sentence_2,
          'label_eng': lab}
  df = pd.DataFrame(raw_data_train, columns = ['sentence1_eng','sentence2_eng','label_eng'])
  return df

def get_data_hindi(a):
  b_ = list(a['gold_label'])
  lab = []
  """
  lab  = []
  for i in b_:
    lab.append(i-1)
  """
  for i in b_:
    if i=='contradiction':
        lab.append(0)
        
    elif i=='neutral':
        lab.append(1)
    elif i== 'entailment':
        lab.append(2)
    else:
        lab.append(3)
  sentence_1 = list(a['premise_hindi'])
  sentence_2 = list(a['hypo_hindi'])
  raw_data_train = {'sentence1_hindi': sentence_1, 
              'sentence2_hindi': sentence_2,
          'label_hindi': lab}
  df = pd.DataFrame(raw_data_train, columns = ['sentence1_hindi','sentence2_hindi','label_hindi'])
  return df

train_eng = get_data_eng(train)
train_hindi = get_data_hindi(train)

test_eng = get_data_eng(test)
test_hindi = get_data_hindi(test)

train_eng[0:10]

train_hindi[0:10]

test_eng[0:10]

test_hindi[0:10]

label_list = [0,1,2,3]

train_InputExamples_eng = train_eng.apply(lambda x: bert.run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a = x['sentence1_eng'], 
                                                                   text_b = x['sentence2_eng'], 
                                                                   label = x['label_eng']), axis = 1)
train_InputExamples_hindi = train_hindi.apply(lambda x: bert.run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a = x['sentence1_hindi'], 
                                                                   text_b = x['sentence2_hindi'], 
                                                                   label = x['label_hindi']), axis = 1)

test_InputExamples_eng = test_eng.apply(lambda x: bert.run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a = x['sentence1_eng'], 
                                                                   text_b = x['sentence2_eng'], 
                                                                   label = x['label_eng']), axis = 1)
test_InputExamples_hindi = test_hindi.apply(lambda x: bert.run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a = x['sentence1_hindi'], 
                                                                   text_b = x['sentence2_hindi'], 
                                                                   label = x['label_hindi']), axis = 1)

vocab_file = "multi_cased_L-12_H-768_A-12/vocab.txt"
def create_tokenizer_from_hub_module():
 
  return bert.tokenization.FullTokenizer(
      vocab_file=vocab_file, do_lower_case=True)

tokenizer = create_tokenizer_from_hub_module()

tokenizer.tokenize("how are you")

tokenizer.tokenize("एक आदमी गोरा सिर वाली महिला से बात कर रहा है।")

MAX_SEQ_LENGTH = 128
# Convert our train and test features to InputFeatures that BERT understands.
train_features_eng = bert.run_classifier.convert_examples_to_features(train_InputExamples_eng, label_list, MAX_SEQ_LENGTH, tokenizer)
train_features_hindi = bert.run_classifier.convert_examples_to_features(train_InputExamples_hindi, label_list, MAX_SEQ_LENGTH, tokenizer)

MAX_SEQ_LENGTH = 128
# Convert our train and test features to InputFeatures that BERT understands.
test_features_eng = bert.run_classifier.convert_examples_to_features(test_InputExamples_eng, label_list, MAX_SEQ_LENGTH, tokenizer)
test_features_hindi = bert.run_classifier.convert_examples_to_features(test_InputExamples_hindi, label_list, MAX_SEQ_LENGTH, tokenizer)

def create_model(bert_config, is_training, input_ids, input_mask, segment_ids,
                 labels, num_labels, use_one_hot_embeddings):
  """Creates a classification model."""
  model = bert.run_classifier.modeling.BertModel(
      config=bert_config,
      is_training=is_training,
      input_ids=input_ids,
      input_mask=input_mask,
      token_type_ids=segment_ids,
      use_one_hot_embeddings=use_one_hot_embeddings)

  # In the demo, we are doing a simple classification task on the entire
  # segment.
  #
  # If you want to use the token-level output, use model.get_sequence_output()
  # instead.
  output_layer = model.get_pooled_output()
  hidden_size = output_layer.shape[-1].value

  output_weights = tf.get_variable(
      "output_weights", [num_labels, hidden_size],
      initializer=tf.truncated_normal_initializer(stddev=0.02))

  output_bias = tf.get_variable(
      "output_bias", [num_labels], initializer=tf.zeros_initializer())

  with tf.variable_scope("loss"):
    if is_training:
      # I.e., 0.1 dropout
      output_layer = tf.nn.dropout(output_layer, keep_prob=0.9)

    logits = tf.matmul(output_layer, output_weights, transpose_b=True)
    logits = tf.nn.bias_add(logits, output_bias)
    probabilities = tf.nn.softmax(logits, axis=-1)
    log_probs = tf.nn.log_softmax(logits, axis=-1)
    predicted_labels = tf.squeeze(tf.argmax(log_probs, axis=-1, output_type=tf.int32))

    one_hot_labels = tf.one_hot(labels, depth=num_labels, dtype=tf.float32)

    per_example_loss = -tf.reduce_sum(one_hot_labels * log_probs, axis=-1)
    loss = tf.reduce_mean(per_example_loss)

    return (loss, per_example_loss, logits, probabilities,predicted_labels,output_layer)

import numpy as np

def model_fn_builder(bert_config, num_labels, init_checkpoint, learning_rate,
                     num_train_steps, num_warmup_steps, use_tpu,
                     use_one_hot_embeddings):
  """Returns `model_fn` closure for TPUEstimator."""

  def model_fn(features, labels, mode, params):  # pylint: disable=unused-argument
    """The `model_fn` for TPUEstimator."""

    tf.logging.info("*** Features ***")
    for name in sorted(features.keys()):
      tf.logging.info("  name = %s, shape = %s" % (name, features[name].shape))

    input_ids = features["input_ids"]
    input_mask = features["input_mask"]
    segment_ids = features["segment_ids"]
    label_ids = features["label_ids"]
    is_real_example = None
    if "is_real_example" in features:
      is_real_example = tf.cast(features["is_real_example"], dtype=tf.float32)
    else:
      is_real_example = tf.ones(tf.shape(label_ids), dtype=tf.float32)

    is_training = (mode == tf.estimator.ModeKeys.TRAIN)

    (total_loss, per_example_loss, logits, probabilities,predicted_labels,hidden_context) = create_model(
        bert_config, is_training, input_ids, input_mask, segment_ids, label_ids,
        num_labels, use_one_hot_embeddings)

    tvars = tf.trainable_variables()
    initialized_variable_names = {}
    scaffold_fn = None
    if init_checkpoint:
      (assignment_map, initialized_variable_names
      ) = bert.run_classifier.modeling.get_assignment_map_from_checkpoint(tvars, init_checkpoint)
      if use_tpu:

        def tpu_scaffold():
          tf.train.init_from_checkpoint(init_checkpoint, assignment_map)
          return tf.train.Scaffold()

        scaffold_fn = tpu_scaffold
      else:
        tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

    tf.logging.info("**** Trainable Variables ****")
    for var in tvars:
      init_string = ""
      if var.name in initialized_variable_names:
        init_string = ", *INIT_FROM_CKPT*"
      tf.logging.info("  name = %s, shape = %s%s", var.name, var.shape,
                      init_string)

    output_spec = None
    if mode == tf.estimator.ModeKeys.TRAIN:

      train_op = optimization.create_optimizer(
          total_loss, learning_rate, num_train_steps, num_warmup_steps, use_tpu)

      output_spec = tf.estimator.EstimatorSpec(
          mode=mode,
          loss=total_loss,
          train_op=train_op)
    elif mode == tf.estimator.ModeKeys.EVAL:

      def metric_fn(per_example_loss, label_ids, logits, is_real_example):
        predictions = tf.argmax(logits, axis=-1, output_type=tf.int32)
        accuracy = tf.metrics.accuracy(
            labels=label_ids, predictions=predictions, weights=is_real_example)
        loss = tf.metrics.mean(values=per_example_loss, weights=is_real_example)
       
        return {
            "eval_accuracy": accuracy,
            "eval_loss": loss
        }

      eval_metrics = metric_fn(per_example_loss, label_ids, logits, is_real_example)
      
      output_spec = tf.estimator.EstimatorSpec(
          mode=mode,
          loss=total_loss,
          eval_metric_ops=eval_metrics)
    else:
      output_spec = tf.estimator.EstimatorSpec(
          mode=mode,
          predictions={"probabilities": probabilities,"labels": predicted_labels, "hidden_context": hidden_context})
    return output_spec

  return model_fn

def create_model_progressive(bert_config, is_training, input_ids, input_mask, segment_ids,
                 labels, num_labels, use_one_hot_embeddings,hidden_context):
  """Creates a classification model."""
  model = bert.run_classifier.modeling.BertModel(
      config=bert_config,
      is_training=is_training,
      input_ids=input_ids,
      input_mask=input_mask,
      token_type_ids=segment_ids,
      use_one_hot_embeddings=use_one_hot_embeddings)

  # In the demo, we are doing a simple classification task on the entire
  # segment.
  #
  # If you want to use the token-level output, use model.get_sequence_output()
  # instead.
  output_layer = model.get_pooled_output()

  hidden_size = output_layer.shape[-1].value

  output_weights = tf.get_variable(
      "output_weights", [num_labels, hidden_size],
      initializer=tf.truncated_normal_initializer(stddev=0.02))

  output_bias = tf.get_variable(
      "output_bias", [num_labels], initializer=tf.zeros_initializer())

  with tf.variable_scope("loss"):
    if is_training:
      # I.e., 0.1 dropout
      output_layer = tf.nn.dropout(output_layer, keep_prob=0.9)


    output_layer_probs = tf.nn.softmax(output_layer,axis = -1)
    #loss = y_true * log(y_true / y_pred)
    hidden_context = tf.nn.softmax(hidden_context,axis = -1)
    per_example_kd_loss = tf.keras.losses.KLD(hidden_context,output_layer_probs)

    logits = tf.matmul(output_layer, output_weights, transpose_b=True)
    logits = tf.nn.bias_add(logits, output_bias)
    probabilities = tf.nn.softmax(logits, axis=-1)
    log_probs = tf.nn.log_softmax(logits, axis=-1)
    predicted_labels = tf.squeeze(tf.argmax(log_probs, axis=-1, output_type=tf.int32))

    one_hot_labels = tf.one_hot(labels, depth=num_labels, dtype=tf.float32)

    per_example_loss = -tf.reduce_sum(one_hot_labels * log_probs, axis=-1)

    kd_loss_weight = 0.2 #hyperparameter
    per_example_kd_loss = kd_loss_weight*per_example_kd_loss

    per_example_loss += per_example_kd_loss

    

    loss = tf.reduce_mean(per_example_loss)

    return (loss, per_example_loss, logits, probabilities,predicted_labels)

def model_fn_builder_progressive(bert_config, num_labels, init_checkpoint, learning_rate,
                     num_train_steps, num_warmup_steps, use_tpu,
                     use_one_hot_embeddings):
  """Returns `model_fn` closure for TPUEstimator."""

  def model_fn(features, labels, mode, params):  # pylint: disable=unused-argument
    """The `model_fn` for TPUEstimator."""

    tf.logging.info("*** Features ***")
    for name in sorted(features.keys()):
      tf.logging.info("  name = %s, shape = %s" % (name, features[name].shape))

    input_ids = features["input_ids"]
    input_mask = features["input_mask"]
    segment_ids = features["segment_ids"]
    label_ids = features["label_ids"]
    hidden_context = features["hidden_context"]
    is_real_example = None
    if "is_real_example" in features:
      is_real_example = tf.cast(features["is_real_example"], dtype=tf.float32)
    else:
      is_real_example = tf.ones(tf.shape(label_ids), dtype=tf.float32)

    is_training = (mode == tf.estimator.ModeKeys.TRAIN)

    (total_loss, per_example_loss, logits, probabilities,predicted_labels) = create_model_progressive(
        bert_config, is_training, input_ids, input_mask, segment_ids, label_ids,
        num_labels, use_one_hot_embeddings,hidden_context)

    tvars = tf.trainable_variables()
    initialized_variable_names = {}
    scaffold_fn = None
    if init_checkpoint:
      (assignment_map, initialized_variable_names
      ) = bert.run_classifier.modeling.get_assignment_map_from_checkpoint(tvars, init_checkpoint)
      if use_tpu:

        def tpu_scaffold():
          tf.train.init_from_checkpoint(init_checkpoint, assignment_map)
          return tf.train.Scaffold()

        scaffold_fn = tpu_scaffold
      else:
        tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

    tf.logging.info("**** Trainable Variables ****")
    for var in tvars:
      init_string = ""
      if var.name in initialized_variable_names:
        init_string = ", *INIT_FROM_CKPT*"
      tf.logging.info("  name = %s, shape = %s%s", var.name, var.shape,
                      init_string)

    output_spec = None
    if mode == tf.estimator.ModeKeys.TRAIN:

      train_op = optimization.create_optimizer(
          total_loss, learning_rate, num_train_steps, num_warmup_steps, use_tpu)

      output_spec = tf.estimator.EstimatorSpec(
          mode=mode,
          loss=total_loss,
          train_op=train_op)
    elif mode == tf.estimator.ModeKeys.EVAL:

      def metric_fn(per_example_loss, label_ids, logits, is_real_example):
        predictions = tf.argmax(logits, axis=-1, output_type=tf.int32)
        accuracy = tf.metrics.accuracy(
            labels=label_ids, predictions=predictions, weights=is_real_example)
        loss = tf.metrics.mean(values=per_example_loss, weights=is_real_example)
        return {
            "eval_accuracy": accuracy,
            "eval_loss": loss,
        }

      eval_metrics = metric_fn(per_example_loss, label_ids, logits, is_real_example)
      
      output_spec = tf.estimator.EstimatorSpec(
          mode=mode,
          loss=total_loss,
          eval_metric_ops=eval_metrics)
    else:
      output_spec = tf.estimator.EstimatorSpec(
          mode=mode,
          predictions={"probabilities": probabilities,"labels": predicted_labels})
    return output_spec

  return model_fn

def input_fn_builder(features, hidden_context,seq_length, is_training, drop_remainder):
  """Creates an `input_fn` closure to be passed to TPUEstimator."""

  all_input_ids = []
  all_input_mask = []
  all_segment_ids = []
  all_label_ids = []

  for feature in features:
    all_input_ids.append(feature.input_ids)
    all_input_mask.append(feature.input_mask)
    all_segment_ids.append(feature.segment_ids)
    all_label_ids.append(feature.label_id)

  def input_fn(params):
    """The actual input function."""
    batch_size = params["batch_size"]

    num_examples = len(features)
    hidden_shape = hidden_context.shape[-1]
    # This is for demo purposes and does NOT scale to large data sets. We do
    # not use Dataset.from_generator() because that uses tf.py_func which is
    # not TPU compatible. The right way to load data is with TFRecordReader.
    d = tf.data.Dataset.from_tensor_slices({
        "input_ids":
            tf.constant(
                all_input_ids, shape=[num_examples, seq_length],
                dtype=tf.int32),
        "input_mask":
            tf.constant(
                all_input_mask,
                shape=[num_examples, seq_length],
                dtype=tf.int32),
        "segment_ids":
            tf.constant(
                all_segment_ids,
                shape=[num_examples, seq_length],
                dtype=tf.int32),
        "label_ids":
            tf.constant(all_label_ids, shape=[num_examples], dtype=tf.int32),

        "hidden_context":
            tf.constant(hidden_context, shape = [num_examples,hidden_shape], dtype = tf.float32),
    })

    if is_training:
      d = d.repeat()
      d = d.shuffle(buffer_size=100)

    d = d.batch(batch_size=batch_size, drop_remainder=drop_remainder)
    return d

  return input_fn

# Commented out IPython magic to ensure Python compatibility.
def train(output_dir,input_fn,input_fn_builder_progressive = False,hidden_context = None):


  CONFIG_FILE = "multi_cased_L-12_H-768_A-12/bert_config.json"
  INIT_CHECKPOINT = "multi_cased_L-12_H-768_A-12/bert_model.ckpt"

  BATCH_SIZE = 28
  LEARNING_RATE = 2e-5
  NUM_TRAIN_EPOCHS = 2
  # Warmup is a period of time where hte learning rate 
  # is small and gradually increases--usually helps training.
  WARMUP_PROPORTION = 0.1
  # Model configs
  SAVE_CHECKPOINTS_STEPS = 1500
  SAVE_SUMMARY_STEPS = 100
  OUTPUT_DIR = output_dir
  # Compute # train and warmup steps from batch size
  num_train_steps = int(len(input_fn) / BATCH_SIZE * NUM_TRAIN_EPOCHS)
  num_warmup_steps = int(num_train_steps * WARMUP_PROPORTION)
  print(num_train_steps)
  run_config = tf.estimator.RunConfig(
      model_dir=OUTPUT_DIR,
      save_summary_steps=SAVE_SUMMARY_STEPS,
      save_checkpoints_steps=SAVE_CHECKPOINTS_STEPS)

  # Specify outpit directory and number of checkpoint steps to save
  if input_fn_builder_progressive==False:
  


    model_fn = model_fn_builder(
      bert_config=bert.run_classifier.modeling.BertConfig.from_json_file(CONFIG_FILE),
      num_labels=4, #number of unique labels
      init_checkpoint=INIT_CHECKPOINT,
      learning_rate=LEARNING_RATE,
      num_train_steps=num_train_steps,
      num_warmup_steps=num_warmup_steps,
      use_tpu=False,
      use_one_hot_embeddings=False
    )



    estimator = tf.estimator.Estimator(
      model_fn=model_fn,
      config=run_config,
      params={"batch_size": BATCH_SIZE})

  
  
    train_input_fn = bert.run_classifier.input_fn_builder(
        features=input_fn,
        seq_length=MAX_SEQ_LENGTH,
        is_training=True,
        drop_remainder=False)
    

  else:

    model_fn_pr = model_fn_builder_progressive(
      bert_config=bert.run_classifier.modeling.BertConfig.from_json_file(CONFIG_FILE),
      num_labels=4, #number of unique labels
      init_checkpoint=INIT_CHECKPOINT,
      learning_rate=LEARNING_RATE,
      num_train_steps=num_train_steps,
      num_warmup_steps=num_warmup_steps,
      use_tpu=False,
      use_one_hot_embeddings=False
    )



    estimator = tf.estimator.Estimator(
      model_fn=model_fn_pr,
      config=run_config,
      params={"batch_size": BATCH_SIZE})

  
    train_input_fn = input_fn_builder(
        features=input_fn,
        hidden_context=hidden_context,
        seq_length=MAX_SEQ_LENGTH,
        is_training=True,
        drop_remainder=False)

  print(f'Beginning Training!')
#   %timeit

  estimator.train(input_fn=train_input_fn, max_steps=num_train_steps)
  return estimator

def evaluate_and_get_hidden_context(estimator,input_fn_for_test,input_fn_for_hidden,is_progressive = False,hidden_context=None):
  MAX_SEQ_LENGTH = 128
 
  if not is_progressive:
    test_input_fn = run_classifier.input_fn_builder(
      features=input_fn_for_test,
      seq_length=MAX_SEQ_LENGTH,
      is_training=False,
      drop_remainder=False)
     
    estimator.evaluate(input_fn=test_input_fn, steps=None)
    hidden_input_fn = run_classifier.input_fn_builder(
        features=input_fn_for_hidden,
        seq_length=MAX_SEQ_LENGTH,
        is_training=False,
        drop_remainder=False)
    res = estimator.predict(hidden_input_fn)
    hidden_context = []
    for i in res:
      hidden_context.append(i["hidden_context"])
    hidden_context = np.array(hidden_context)
    return hidden_context
  else:
    test_input_fn = input_fn_builder(
      features=input_fn_for_test,
      hidden_context=hidden_context,
      seq_length=MAX_SEQ_LENGTH,
      is_training=False,
      drop_remainder=False)
    estimator.evaluate(input_fn=test_input_fn, steps=None)

estimator = train('out_dir_train_eng',train_features_eng,input_fn_builder_progressive = False,hidden_context = None)

hidden_context_eng = evaluate_and_get_hidden_context(estimator,input_fn_for_test = test_features_eng,input_fn_for_hidden = train_features_eng,is_progressive = False)

estimator = train('out_dir_train_hindi',train_features_hindi,input_fn_builder_progressive = False,hidden_context = None)

hidden_context_hindi = evaluate_and_get_hidden_context(estimator,input_fn_for_test = test_features_hindi,input_fn_for_hidden = train_features_hindi,is_progressive = False)

#progressive training and evaluation

estimator = train('out_dir_train_eng_pr',train_features_eng,input_fn_builder_progressive = True,hidden_context = hidden_context_hindi)

dummy = np.random.randn(4000,768)
h = evaluate_and_get_hidden_context(estimator,input_fn_for_test = test_features_eng,input_fn_for_hidden = train_features_eng,is_progressive = True,hidden_context=dummy)

print(h)

estimator = train('out_dir_train_hindi_pr1',train_features_hindi,input_fn_builder_progressive = True,hidden_context = hidden_context_eng)

dummy = np.random.randn(4000,768)
#dummy = hidden_context_eng[22000:26000,:]
h = evaluate_and_get_hidden_context(estimator,input_fn_for_test = test_features_hindi,input_fn_for_hidden = train_features_hindi,is_progressive = True,hidden_context=dummy)

hidden_context_eng.shape

h

