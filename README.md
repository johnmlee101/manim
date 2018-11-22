TEST

#Manim
[![CircleCI](https://circleci.com/gh/eulertour/manim.svg?style=shield)](https://circleci.com/gh/eulertour/manim)
[![Documentation Status](https://readthedocs.org/projects/manim/badge/?version=latest)](https://manim.readthedocs.io/en/latest/?badge=latest)

Animation engine for explanatory math videos.

I made this fork in an effort to clean up the technical debt that has been accumulating on the upstream repo. Manim has the potential to be an excellent teaching tool, but it needs some work in terms of testing, documentation, community support, and general robustness before that happens.

You can probably tell from the previous paragraph that this project is very much a work in progress. You'll have to do a lot of exploration on your own to learn how the software works. Expect things to break frequently and unexpectedly early on, and to spend some time debugging. Feel free to file an issue if something seems wrong, and I'll get back to you as soon as possible.

## Installation requirements
This fork of Manim runs on python 3.7 only. Earlier versions of python are not supported.
You can install the python dependencies with `pip install -r requirements.txt`.

Manim relies on system libraries you will need to install on your operating system:
* ffmpeg
* latex
* sox

Then you can install the python dependencies:
```sh
python3 -m pip install -r requirements.txt
```
The dockerfile is (should be) the definitive source for all of Manim's requirements.

## How to Use
Todd Zimmerman put together a [very nice tutorial](https://talkingphysics.wordpress.com/2018/06/11/learning-how-to-animate-videos-using-manim-series-a-journey/) on getting started with manim.  I can't make promises that future versions will always be compatible with what is discussed in that tutorial, but he certainly does a much better job than Grant has laying out the basics.

Documentation is in progress [here](https://manim.readthedocs.io/en/latest/index.html).

Try running the following:
```sh
python3 extract_scene.py example_scenes.py SquareToCircle -pl
```

The -p is for previewing, meaning the the video file will
automatically open when it is done rendering.
Use -l for a faster rendering at a lower quality.
Use -s to skip to the end and just show the final frame.
Use -n (number) to skip ahead to the n'th animation of a scene.
Use -f to show the file in finder (for osx)

Look through the old_projects folder to see the code for previous 3b1b videos.  Note, however, that developments are often made to the library without considering backwards compatibility on those old_projects.  To run them with a guarantee that they will work, you will have to go back to the commit which completed that project.

While developing a scene, the `-s` flag is helpful to just see what things look like at the end without having to generate the full animation.  It can also be helpful to use the `-n` flag to skip over some number of animations.

Scenes with `PiCreatures` are somewhat 3b1b specific, so the specific designs for various expressions are not part of the public repository. You should still be able to run them, but they will fall back on using the "plain" expression for the creature.

## Docker Method
Since it's a bit tricky to get all the dependencies set up just right, there is a Dockerfile provided in this repo as well as [a premade image on Docker Hub](https://hub.docker.com/r/eulertour/manim/tags/). This is the image CircleCI uses to run tests.

The image does not contain a copy of the repo. This is intentional, as it allows you to either bind mount a repo that you've cloned locally or clone whichever branch you want. Since test coverage is painfully lacking, the image may not have dependencies for all of manim.

1. [Install Docker](https://www.docker.com/products/overview)
2. Get the docker image
  * Pull it (recommended): `docker pull eulertour/manim:latest`, or
  * Build it: `docker build -t manim .`
3. Run it!
  * Bind mount a local repo (recommended): `docker run -itv /path/to/your/local/manim/repo:/root/manim eulertour/manim` or
  * Clone a remote repo: `docker run -it eulertour/manim`, then `git clone https://github.com/eulertour/manim.git`

Note that the image doesn't have any development tools installed. It purpose is building/testing only.

## Contributing
Is always welcome. In particular, there is still a dire need for tests.

## License
All files in the directories active_projects and old_projects, which by and large generate the visuals for 3b1b videos, are copyright 3Blue1Brown.

The general purpose animation code found in the remainder of the repository, on the other hand, is under the MIT license.
