# Part 0. Before we start

In this guide we'll be working with real training code, so let's check that your computer's up to it.

## What you'll need

For the whole guide, you'll need **a computer running Linux, with an NVIDIA graphics card**. In more detail:

- **Linux.** We used Ubuntu 22.04.
- **An NVIDIA graphics card**, with its driver at version 580 or newer. We used an RTX 5080. The training itself needed about 2 GB of
  its memory.
- **About 15 GB of disk space**, to be comfortable.
- **A decent internet connection** for the installation, which downloads a few gigabytes. Ours took three quarters of an hour, so it's a
  good thing to do the day before.

To find out which card and driver you've got, open a terminal and run:

```bash
nvidia-smi
```

If that prints a table, look for `Driver Version` along the top. If it says the command isn't found, then either you don't have an NVIDIA
card, or its driver isn't installed yet.

## What you should know already

You don't need any experience with reinforcement learning, or robots. It'll help if you've used a terminal before, at least to move
between folders and run a command. We'll explain the rest as we go.

## If you don't have an NVIDIA card

You can still follow quite a bit of this. Driving a policy around in our viewer, checking one and exporting one all run on an ordinary
processor. Training and recording videos need the card, and those parts say so at the top. You're welcome to read along with our
results, and the policies that we trained come with this guide, so you can try those out instead.

## How long will it take?

Apart from the installation, you can have the robot walking around on your screen in a few minutes. The experiment in Parts 3 and 4 is two
training runs, which were about a quarter of an hour each on our computer. Most of that time you'll be waiting, so you can leave it running
and come back.

## Up next

In [Part 1](01_setting_up.md) we'll get the code and install it.
