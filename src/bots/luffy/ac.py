"""
solving pendulum using actor-critic model
"""

import gym
import numpy as np
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras.layers.merge import Add, Multiply
from keras.optimizers import Adam
import keras.backend as K

import tensorflow as tf

import random
from collections import deque

from bot import BaseBot, GameInfo
from card import INDEX_TO_SUIT
# determines how to assign values to each state, i.e. takes the state
# and action (two-input model) and determines the corresponding value
class Luffy(BaseBot):

    MODEL_PATH = './cache/models/AC/'
    LEARNING_RATE=0.001
    GAMMA = 0.9

    def __init__(self, sess, scope, queue, is_restore=True, output_graph=True, output_summary=True):
        self.is_restore = is_restore
        self.output_graph = output_graph
        self.output_summary = output_summary
        self.episode = 0
        self.memory = deque()
        self.n_features = BaseBot.N_FEATURES
        self.n_actions = BaseBot.N_ACTIONS
        self.sess = sess
        self.queue = queue
        self.saver = None
        with tf.variable_scope(scope):
            self.actor = Actor(self.sess, scope, self.n_features, self.n_actions)
            self.critic = Critic(self.sess, scope, self.n_features)

        if is_restore:
            self.saver = tf.train.Saver()
            print("restore from %r" % Luffy.MODEL_PATH)
            ckpt = tf.train.get_checkpoint_state(Luffy.MODEL_PATH)
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)
        else:
            self.sess.run(tf.global_variables_initializer())

    def store_transition(self, s: tuple):
        """
        s, a, r, s_
        """
        (state, action, reward, state_) = s
        self.memory.append(s)

    def declare_action(self, info: GameInfo):
        state = info.to_array().reshape(1, self.n_features)
        prob_weights = self.actor.declare_action(state)

        for index_suit, s in enumerate(INDEX_TO_SUIT):
            for i in range(2, 15):
                if info.candidate.df.loc[i, s] == 0:
                    prob_weights[0][index_suit * 13 + i -2] = 0
        prob_weights = prob_weights / prob_weights.sum()
        action = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())  # select action w.r.t the actions prob
        return action

    def learn(self, episode):
        (state, action, reward, state_) = self.memory.popleft()
        td_error = self.critic.learn(self.episode, state, reward, state_)
        self.actor.learn(self.episode, state, action, td_error)

        # put grad in here
        self.queue.put([self.actor.grad_and_var, self.critic.grad_and_var])

        if episode % BaseBot.STORE_MODEL_FREQUENCY is 0:
            if self.saver is None:
                self.saver = tf.train.Saver()
            ckpt = tf.train.get_checkpoint_state(Luffy.MODEL_PATH)
            self.saver.save(self.sess, Luffy.MODEL_PATH + '/model_' + str(episode) + '.ckpt')
            print("Saving Model with episode %r " % episode)

        """
        if episode % BaseBot.UPDATE_FREQUENCY == 0:
            self.writer.add_summary(self.summary, episode)
            self.writer.flush()
            print("summary flushed")
        """

class GlobalAC:

    def __init__(self, sess, n_features, n_actions, queue, learning_rate=Luffy.LEARNING_RATE, scope='Global_Net'):
        self.sess = sess
        self.queue = queue
        with tf.variable_scope(scope):
            self.s = tf.placeholder(tf.float32, [None, n_features], 'state')
            self.actor_parameter  = Actor(self.sess, scope, n_features, n_actions, lr=learning_rate).parameter
            self.critic_parameter = Critic(self.sess, scope, n_features, lr=learning_rate).parameter
        pass

    def push_global(self):
        pass

    def pull_global(self):
        pass


class Actor:

    def __init__(self, sess, scope, n_features, n_actions, lr=Luffy.LEARNING_RATE):
        self.sess = sess
        self.scope = scope
        self.n_features = n_features
        self.n_actions = n_actions
        self.lr = lr
        self.parameter = None
        self.grad_and_var = None
        self._build_net()

    def declare_action(self, state):
        prob_weights = self.sess.run(self.acts_prob, {self.s: state})
        return prob_weights

    def learn(self, episode, state, action, td):
        feed_dict = {self.s: state, self.a: action, self.td_error: td}
        _, exp_v = self.sess.run([self.train_op, self.exp_v], feed_dict)
        return exp_v

    def _build_net(self):
        self.s = tf.placeholder(tf.float32, [1, self.n_features], "state")
        self.a = tf.placeholder(tf.int32, None, "act")
        self.td_error = tf.placeholder(tf.float32, None, "td_error")  # TD_error

        with tf.variable_scope(self.scope + '/actor'):
            l1 = tf.layers.dense(
                inputs=self.s,
                units=200,    # number of hidden units
                activation=tf.nn.relu,
                kernel_initializer=tf.random_normal_initializer(0., .1),    # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='l1'
            )

            self.acts_prob = tf.layers.dense(
                inputs=l1,
                units=self.n_actions,    # output units
                activation=tf.nn.softmax,   # get action probabilities
                kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='acts_prob'
            )

        with tf.variable_scope('exp_v'):
            log_prob = tf.log(self.acts_prob[0, self.a])
            self.exp_v = tf.reduce_mean(log_prob * self.td_error)  # advantage (TD_error) guided loss

        with tf.variable_scope('train'):
            # self.train_op = tf.train.AdamOptimizer(lr).minimize(-self.exp_v)  # minimize(-exp_v) = maximize(exp_v)
            optimizer = tf.train.AdamOptimizer(self.lr)
            self.grad_and_var = optimizer.compute_gradients(-self.exp_v)  # minimize(-exp_v) = maximize(exp_v)
            self.train_op = optimizer.apply_gradients(self.grad_and_var)
        self.parameter = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.scope + '/actor')


class Critic:

    def __init__(self, sess, scope, n_features, lr=Luffy.LEARNING_RATE):
        self.sess = sess
        self.scope = scope
        self.n_features = n_features
        self.lr = lr
        self.parameter = None
        self.grad_and_var = None
        self._build_net()

    def learn(self, episode, state, reward, state_):
        v_ = self.sess.run(self.v, {self.s:state_})
        td_error, _ = self.sess.run([self.td_error, self.train_op],
                                    {self.s: state, self.v_: v_, self.r: reward})
        return td_error

    def _build_net(self):
        self.s = tf.placeholder(tf.float32, [1, self.n_features], "state")
        self.v_ = tf.placeholder(tf.float32, [1, 1], "v_next")
        self.r = tf.placeholder(tf.float32, None, 'r')

        with tf.variable_scope(self.scope + '/critic'):
            l1 = tf.layers.dense(
                inputs=self.s,
                units=200,  # number of hidden units
                activation=tf.nn.relu,  # None
                # have to be linear to make sure the convergence of actor.
                # But linear approximator seems hardly learns the correct Q.
                kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='l1'
            )

            self.v = tf.layers.dense(
                inputs=l1,
                units=1,  # output units
                activation=None,
                kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='V'
            )

        with tf.variable_scope('squared_TD_error'):
            self.td_error = self.r + Luffy.GAMMA * self.v_ - self.v
            self.loss = tf.square(self.td_error)    # TD_error = (r+gamma*V_next) - V_eval
        with tf.variable_scope('train'):
            # self.train_op = tf.train.AdamOptimizer(lr).minimize(self.loss)
            optimizer = tf.train.AdamOptimizer(self.lr)
            self.grad_and_var = optimizer.compute_gradients(self.loss)
            self.train_op = optimizer.apply_gradients(self.grad_and_var)

        self.parameter = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.scope + '/critic')
