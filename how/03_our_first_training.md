# Part 3. Our first training

> **You'll need an NVIDIA card for this part.**

Until now we've only been using policies. In this part we're going to train one. We'll cover:

- What we're starting from, and what a recipe is
- Trying out a tiny training run, to make sure that everything works
- Starting a proper one, and making sense of what it prints
- Watching its progress on a graph

As usual, in a new terminal:

```bash
cd ~/mini_pupper_4_rl
unset PYTHONPATH
```

## Where we're starting from

We won't be teaching the robot to walk from nothing. As we saw in [Chapter 1](../why/01_a_head_start.md), that's a hard way to do it,
and the trainer in this repository doesn't even have the option. What it does instead is carry on from a walker that already exists, and teach
it something more. It's called [fine-tuning](../why/05_learning_without_forgetting.md#what-if-the-robot-changes).

The walker we'll carry on from comes with the code, and it's a decent one, but a bit slow. It was trained to go up to 0.12 m/s, and to turn at 1
radian per second. The released walker, which is the one that we drove around in Part 2, got to 0.20 m/s and 2 radians per second, in four
stages of training. We're going to have a go at the beginning of the first stage.

## What's a recipe?

A training run has an awful lot of settings. Rather than typing them all in, we keep them together in a small script, which we call a **recipe**.
Let's have a look at the first one:

```bash
cat mp4_rl/skills/walker/recipes/sku2/step1.sh
```

The top half is a description of what it does, and the bottom half is one enormous command. You don't need to follow all of it, but you might
recognise a few things from the other tutorial: `--anchor` and `--beta0` ([the anchor](../why/01_a_head_start.md#keeping-hold-of-the-trot), which holds the
new policy close to the one it started from, and how strong it is), `--critic-warmup` (more on that soon), `--terrain`, `--progress` ([paying for what we want](../why/03_you_get_what_you_reward.md)), and `--friction`
([different worlds](../why/02_the_simulator_lies_a_little.md#training-on-lots-of-different-worlds)).

## A tiny run

A proper run takes a while, so it's a good habit to start with a tiny one. That way, if something's broken, we find out in a minute:

```bash
ENVS=64 OUT=runs/quick sh mp4_rl/skills/walker/recipes/sku2/step1.sh "" "" 5
```

- `ENVS=64` is how many robots to train with. A normal run has 1,024.
- `OUT=runs/quick` is the folder to put the results in.
- Then come three settings, in order. The first is the [seed](../why/03_you_get_what_you_reward.md#six-robots-learn-to-fall-over), a number that all the random choices come from. The second is the walker to
  start from. We've left both of them empty (`""`), which means we're happy with the usual ones. The last is how many **rounds** to do, where a round is all of
  the robots acting for a moment, and then the policy being updated. We only want 5.

It took just over a minute on our computer. It'll print a lot, including some warnings, and we'll come to what it all means shortly. If all's well,
it finishes like this:

```
RUN_DIR runs/quick/<date and time>_s71_step1
```

There may be a warning about "pending keyframes" after it, which is harmless. Let's see what we've made:

```bash
ls runs/quick/*/
```

You should find `model_6300.pt` and `model_6301.pt` among the files. These are **checkpoints**, so snapshots of the networks during training. The numbers carry on from
the walker we started with, which had already done 6,297 rounds.

Don't expect this one to have learned anything, though! For the first few rounds
[only the critic is trained](../why/01_a_head_start.md#one-step-forward-all-the-steps-back). That's a second network that judges how well things are going, and it needs to know what it's
talking about before it starts giving advice. In this recipe that's the first 30 rounds. We only did five, so our "new" policy is the old one.

## The real thing

Now that we know it works, let's do 300 rounds:

```bash
OUT=runs/plain sh mp4_rl/skills/walker/recipes/sku2/step1.sh "" "" 300
```

This took about a quarter of an hour for us. If you get a message about running out of memory, try it with fewer robots by adding `ENVS=512` at the start (and use the
same number in Part 4, so that the two runs can be compared).

While it's running, it prints a page of numbers after every round. Here are a few of them, from near the end of ours:

```
                          Learning iteration 6590/6597
                    Mean anchor_mse loss: 0.0020
                            Mean reward: 26.33
                    Mean episode length: 535.28
           Episode_Reward/track_lin_vel: 0.7917
              Episode_Reward/swing_apex: -0.0930
    Curriculum/command_range/fwd_vx_max: 0.1983
                          Iteration time: 2.78s
                                     ETA: 00:00:16
```

- **Learning iteration** is which round we're on.
- **Mean anchor_mse** is how far the policy has drifted from the walker we started with, on the movements that it already knew.
- **Mean reward** is the one that everybody looks at. As we found out [the hard way](../why/03_you_get_what_you_reward.md), it isn't the whole story.
- **Mean episode length** is how many control steps the robots last, so at 50 a second, 535 of them is nearly 11 seconds. (Robots on the
  stairs also finish when they get off them.) If it suddenly collapses, something's wrong.
- **Episode_Reward/...** is the reward broken down into its parts. `track_lin_vel` is for moving at the right speed, and `swing_apex` is a penalty for not
  lifting the feet high enough. We'll be seeing more of that one.
- **fwd_vx_max** is the fastest that the robots are being asked to walk. The recipe starts them off at 0.12 m/s and turns it up as they go.
- **ETA** is how long there is to go.

Early on, a lot of the numbers are zero, or look strange. It takes a few rounds for them to settle.

## Watching it on a graph

It's much nicer to look at all that on a graph. The training writes everything down as it goes, and there's a tool called **TensorBoard** that can plot it. Leave the training
running, open a second terminal, and run:

```bash
cd ~/mini_pupper_4_rl
unset PYTHONPATH
.venv/bin/tensorboard --logdir runs
```

Then open [http://localhost:6006](http://localhost:6006) in your browser. You'll find a list of plots down the page. Look for `Train/mean_reward` and
`Train/mean_episode_length`, and you should see them being drawn as the run goes on.

Expect the reward to be a bit jumpy, and don't be surprised if it isn't a nice smooth climb. The job's getting harder the whole time, since the commands are getting faster.

When you've seen enough, press Ctrl+C in that terminal to stop TensorBoard. The training carries on without it.

## Up next

At the end of the run, there should be a `model_6596.pt` in `runs/plain`. On its own it isn't very exciting, but it gives us something to compare with. In
[Part 4](04_changing_one_thing.md), we'll do the same run again, with one thing changed.
