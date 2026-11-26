# Part 1. Setting up

In this part we're going to get everything installed. We'll cover:

- Opening a terminal and getting a couple of tools
- Downloading the code
- Installing it
- Checking that it worked

If you've got ROS on your computer, there's one thing to watch out for, and we'll come to it in a moment.

## Some tools

Open a terminal. First we need **git**, for downloading the code, and **curl**, for downloading other things:

```bash
sudo apt update
sudo apt install git curl
```

Then we need **uv**. The code is written in Python, and it relies on a lot of other people's Python packages, in very particular
versions. uv is a program that fetches them all, and keeps them in a folder of their own so that they don't get mixed up with anything
else on your computer. It's installed like this:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once that's done, close the terminal and open a new one, so that it notices uv is there. Then check:

```bash
uv --version
```

We need 0.12.7 or newer. If yours is older, `uv self update` should bring it up to date.

## Getting the code

Now let's download the code. We'll put it in your home folder:

```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_4_rl.git
cd mini_pupper_4_rl
git checkout 64021d2
```

Going through those:

- `cd ~` goes to your home folder.
- `git clone` makes a copy of the code, in a new folder called `mini_pupper_4_rl`.
- `cd mini_pupper_4_rl` goes into it. **Every command from here on is run from this folder.**
- `git checkout` picks out one particular version, which is the one we wrote this guide with. That way, everything should match even if the
  code changes later.

Git will print a rather worrying message about being in a "detached HEAD" state. All it means is that we're looking at a fixed version,
so you can ignore it.

## Installing

One more thing before we install. If you use ROS, it sets a variable called `PYTHONPATH`, which makes Python pick up the wrong packages, so
we'll clear it. If you don't use ROS, this does nothing:

```bash
unset PYTHONPATH
```

You'll need to do that in each new terminal that you open. Now we can run the installer:

```bash
bash scripts/install/install.sh
```

It looks for an NVIDIA driver to decide what to install. Then it goes and gets it all, so this could take a while, depending on your connection:
ours needed three quarters of an hour. Everything goes into a hidden folder called `.venv`, which ends up at about 6.5 GB.

> **No NVIDIA card?** The installer will notice, and choose a smaller version with everything you need for driving and checking policies. It's
> about 1 GB.

## Did it work?

At the end, the installer checks its own work. You should see something like this:

```
[mp4-rl] verifying ...
python 3.12.14  (.../mini_pupper_4_rl/.venv/bin/python)
  ok   numpy                2.5.3
  ok   scipy                1.18.1
  ...
  torch cuda available: True  (build: 13.0)
  ...
  ok   policy walker sku2   calibration, joint limits and robot model as recorded
  ok   policy getup sku2    calibration, joint limits and robot model as recorded
  ...
[mp4-rl] done. Activate with:  source .../mini_pupper_4_rl/.venv/bin/activate
```

What we're looking for is `ok` on each line, no `FAIL`, and, if you've got an NVIDIA card, `torch cuda available: True`. The last line
suggests activating something, but we won't need to.

If it stopped partway because of the connection, just run the same command again.

CUDA is what lets programs use an NVIDIA card. If it says that it *isn't* available, it's most likely the driver. Have another look at the version that `nvidia-smi` gives you, which needs to be
580 or newer.

There's more about the installer on the repository's
[installation page](https://github.com/mangdangroboticsclub/mini_pupper_4_rl/blob/64021d25e2c31798e64d59916ecb94ed6aa60041/docs/INSTALL.md), if you get stuck or
you're just curious.

## Up next

Now that's out of the way, [let's meet the walker](02_meet_the_walker.md).
