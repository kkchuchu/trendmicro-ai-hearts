"""
This part of code is the reinforcement learning brain, which is a brain of the agent.
All decisions are made in here.
Policy Gradient, Reinforcement Learning.
View more on my tutorial page: https://morvanzhou.github.io/tutorials/
Using:
Tensorflow: 1.0
gym: 0.8.0
"""

import numpy as np
import tensorflow as tf

from bot import BaseBot


class Foo(BaseBot):
    MODEL_PATH = './cache/models/PG/'

    def __init__(
            self,
            n_actions=52,
            n_features=438, # #player * (4 + 52 * 2) + n_game + n_round + 4 * score + start_pos
            learning_rate=0.01,
            reward_decay=0.95,
            is_restore=False,
            output_graph=True,
            output_summary=True,
    ):
        self.output_summary = output_summary
        if self.output_summary:
            self.summary = tf.Summary()

        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay

        self._empty_episode_data()

        self._build_net()

        self.sess = tf.Session()

        self.saver = tf.train.Saver()

        if is_restore:
            print("restore from %r" % Foo.MODEL_PATH)
            ckpt = tf.train.get_checkpoint_state(Foo.MODEL_PATH)
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)

        if output_graph:
            # $ tensorboard --logdir=logs
            # http://0.0.0.0:6006/
            # tf.train.SummaryWriter soon be deprecated, use following
            self.writer = tf.summary.FileWriter("logs/", self.sess.graph)


        self.sess.run(tf.global_variables_initializer())

    def _build_net(self):
        with tf.name_scope('inputs'):
            self.tf_obs = tf.placeholder(tf.float32, [None, self.n_features], name="observations")
            self.tf_acts = tf.placeholder(tf.int32, [None, ], name="actions_num")
            self.tf_vt = tf.placeholder(tf.float32, [None, ], name="actions_value")
        # fc1
        layer = tf.layers.dense(
            inputs=self.tf_obs,
            units=10,
            activation=tf.nn.tanh,  # tanh activation
            kernel_initializer=tf.random_normal_initializer(mean=0, stddev=0.3),
            bias_initializer=tf.constant_initializer(0.1),
            name='fc1'
        )
        # fc2
        all_act = tf.layers.dense(
            inputs=layer,
            units=self.n_actions,
            activation=None,
            kernel_initializer=tf.random_normal_initializer(mean=0, stddev=0.3),
            bias_initializer=tf.constant_initializer(0.1),
            name='fc2'
        )

        self.all_act_prob = tf.nn.softmax(all_act, name='act_prob')  # use softmax to convert to probability

        with tf.name_scope('loss'):
            # to maximize total reward (log_p * R) is to minimize -(log_p * R), and the tf only have minimize(loss)
            neg_log_prob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=all_act, labels=self.tf_acts)   # this is negative log of chosen action
            # or in this way:
            # neg_log_prob = tf.reduce_sum(-tf.log(self.all_act_prob)*tf.one_hot(self.tf_acts, self.n_actions), axis=1)
            loss = tf.reduce_mean(neg_log_prob * self.tf_vt)  # reward guided loss
            if self.output_summary:
                # self.summary.value.add('vt', simple_value=np.mean(self.tf_vt))
                # self.summary.value.add('loss', simple_value=loss)
                pass

        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(self.lr).minimize(loss)

    def declare_action(self, info):
        train_data = info.to_array().reshape(1, self.n_features)
        prob_weights = self.sess.run(self.all_act_prob, feed_dict={self.tf_obs: train_data, }
                                     )
        t = []
        for s in ['S', 'H', 'D', 'C']:
            t = t + info.players[info.me].valid_action.df.loc[:, s].tolist()
        for i, v in enumerate(t):
            if v == 0:
                prob_weights[0][i] = 0
        prob_weights = prob_weights / prob_weights.sum()
        action = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())  # select action w.r.t the actions prob
        return action

    def store_transition(self, s, a, r):
        self.ep_obs.append(s)
        self.ep_as.append(a)
        self.ep_rs.append(r)

    def learn(self, episode):
        # discount and normalize episode reward
        discounted_ep_rs_norm = self._discount_and_norm_rewards()

        # train on episode
        result = self.sess.run(self.train_op, feed_dict={
             self.tf_obs: np.vstack(self.ep_obs),  # shape=[None, n_obs]
             self.tf_acts: np.array(self.ep_as),  # shape=[None, ]
             self.tf_vt: discounted_ep_rs_norm,  # shape=[None, ]
        })
        print(np.mean(self.ep_as))
        # self.summary.value.add('tf_acts/action', np.mean(self.ep_as))
        self._empty_episode_data()
        if episode % BaseBot.STORE_MODEL_FREQUENCY is 0:
            ckpt = tf.train.get_checkpoint_state(Foo.MODEL_PATH)
            self.saver.save(self.sess, Foo.MODEL_PATH + '/model_' + str(episode) + '.ckpt')
            print("Saving Model with episode %r " % episode)

        if episode % BaseBot.UPDATE_FREQUENCY == 0:
            self.writer.add_summary(self.summary, episode)
            self.writer.flush()
            print("summary flushed")

        return discounted_ep_rs_norm

    def _empty_episode_data(self):
        self.ep_obs, self.ep_as, self.ep_rs = [], [], []    # empty episode data

    def _discount_and_norm_rewards(self):
        # discount episode rewards
        discounted_ep_rs = np.zeros_like(self.ep_rs)
        running_add = 0
        for t in reversed(range(0, len(self.ep_rs))):
            running_add = running_add * self.gamma + self.ep_rs[t]
            discounted_ep_rs[t] = running_add

        # normalize episode rewards
        discounted_ep_rs -= np.mean(discounted_ep_rs)
        discounted_ep_rs /= np.std(discounted_ep_rs)
        return discounted_ep_rs
