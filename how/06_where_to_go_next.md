# Part 6. Where to go next

To finish off, here are a few directions you could go in.

## A longer run

> **You'll need an NVIDIA card for this, and for the next section.**

Our runs were cut short at 300 rounds, and the recipe is meant to have 1,000. To do the full thing, leave off the numbers at the end:

```bash
OUT=runs/full sh mp4_rl/skills/walker/recipes/sku2/step1.sh
```

It took 48 minutes on our RTX 5080 with nothing else running, so on a slower card you may want to leave it overnight. Besides having longer to practise, the robots start getting some much harder shoves from round 300 on. You'd end
up with a `model_7296.pt`.

That's the first of four stages that the released walker went through, and the others work the same way. They're described on the
[walker's page](https://github.com/mangdangroboticsclub/mini_pupper_4_rl/blob/64021d25e2c31798e64d59916ecb94ed6aa60041/mp4_rl/skills/walker/README.md), along with the rest of the tests, like shoves, rough ground and stairs. The
[get-up's page](https://github.com/mangdangroboticsclub/mini_pupper_4_rl/blob/64021d25e2c31798e64d59916ecb94ed6aa60041/mp4_rl/skills/getup/README.md) does the same for getting up.

## Other settings

The trainer can list all of its settings. Not all of them come with an explanation, but the names give you some idea:

```bash
.venv/bin/python -m mp4_rl.skills.walker.train --help
```

As we've seen, it's easy to get more than you bargained for, so test every movement and not just the one you care about.

## A policy of your own

If you'd like the robot to do something completely different, you'll need to write some Python. These are the places to look first, all inside `mp4_rl/skills/walker`:

- `task.py` is what the robot is asked to do, and what it's rewarded for. Search for `RewardTermCfg` to find the list of rewards.
- `terrain.py` is the ground it practises on.
- `train.py` is the trainer, and where those settings come from.

A gentle way to start is to change one of the rewards in `task.py`, and do the same comparison that we did in Part 4.

Adding a whole new skill is a much bigger job. The walker's trainer always carries on from an existing walker, so for something new you'd be bringing your own starting point, or
[making one](../why/06_getting_back_up.md#making-our-own-teacher). When you're ready, the repository has a page on
[adding a policy](https://github.com/mangdangroboticsclub/mini_pupper_4_rl/blob/64021d25e2c31798e64d59916ecb94ed6aa60041/docs/ADDING_A_POLICY.md). Or why not see how yours does against everyone else's in the
[Mini Pupper Arena](https://md-robotics-mp4-arena.hf.space/)?

## That's it!

Hopefully you've now got a feel for what it's like to train one of these. If yours has learned to do something daft, welcome to the club. The story of everything that went wrong for us is in
[the other tutorial](../why/README.md).
