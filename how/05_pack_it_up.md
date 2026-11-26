# Part 5. Packing it up

Once we've got a policy that we like, we'd want to take it out of the training code, and put it into a form that a robot can use. In this part we'll cover:

- What exporting does
- Checking an exported policy
- Driving it around

You don't need an NVIDIA card for this part. In a new terminal:

```bash
cd ~/mini_pupper_4_rl
unset PYTHONPATH
```

## If you didn't train one

We've put our own two policies from Part 4 in a file called [policies.zip](policies.zip): one from the plain run, and one that lifts its feet higher. Download it from that link,
then unpack it into `runs/exports`, which is where they'd be if you'd made them yourself:

```bash
mkdir -p runs/exports
.venv/bin/python -m zipfile -e ~/Downloads/policies.zip runs/exports
```

You should now have `runs/exports/plain` and `runs/exports/high`, the same as everybody else. They're only for looking at in simulation, so please don't put them on a robot.

They came from the experiment in [Part 4](04_changing_one_thing.md), so it's worth reading that first if you haven't, to see what we were trying to do. As you'll see, it didn't go entirely
to plan.

## What's in an export?

In Part 4, the export went like this:

```bash
.venv/bin/python -m mp4_rl.common.export runs/high/*/model_6596.pt runs/exports/high
```

As well as the policy, a checkpoint has got the critic, and everything else that's needed for training to carry on. Exporting takes out
[just the policy](../why/07_onto_the_robot.md#packing-for-the-trip), and packs it up with a description of the robot that it's for:

```bash
ls -lh runs/exports/high
```

They're the same four files that we saw in Part 2. All that training comes down to a `policy.npz` of about 800 kilobytes, which is smaller than most photos.

## Checking it

We should check that nothing got lost on the way:

```bash
.venv/bin/python -m mp4_rl.deploy.runner check --policy runs/exports/high
```

The first line of what it prints is the interesting one:

```
fixtures: max |numpy - torch| 3.46e-06 (ok, limit 2.72e-05)
```

During training, the network runs on one set of software (PyTorch), and on the robot it runs on another, much smaller one (NumPy). So the export saves some example observations, along with what the
network said about them at the time. Now the check asks the same questions again, and makes sure that the answers are the same. The difference should be tiny, and yours won't be exactly the same as ours.

The rest of it checks that the policy fits the robot. As before, we're looking for `ok` all the way down.

It doesn't tell us whether the policy's any good, though. Our high-stepping walker passes every one of these checks, and it can't even turn right on the spot!

## Taking it for a drive

Let's try it in the viewer (that's [play.py](play.py) from Part 2):

```bash
.venv/bin/python play.py --policy runs/exports/high
```

Walk forward a bit, and compare it to the plain one:

```bash
.venv/bin/python play.py --policy runs/exports/plain
```

Then press Enter to stop, and try turning on the spot with the left and right arrows. Give them three or four presses, as the high-stepper ignores gentle turns
altogether. With ours, the plain one turns both ways, and the high-stepper only goes left. If you trained your own, you may well find that it's been stubborn
about something else.

## And the real robot?

We'd love you to try out policies on a real robot, but not these ones. They've had 300 rounds of training, and one of them has some strange ideas about turning. The released policies, on the other hand, have been
tested on real hardware, and come with a guide for running them:

- [Running the policies on an SKU2](https://github.com/mangdangroboticsclub/mini_pupper_4_rl/blob/64021d25e2c31798e64d59916ecb94ed6aa60041/mp4_rl/skills/getup/docs/ROBOT_SKU2.md)

## Up next

That's the whole loop: start from something, change it, train it, test it, and pack it up. In [the last part](06_where_to_go_next.md), we'll look at where you could take it from here.
