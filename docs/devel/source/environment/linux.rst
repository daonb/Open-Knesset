===========
Linux
===========

Installing Initial Requirements
=================================

On Linux we'll be creating a clean virtualenv, so in addtion we'll need
developer tools (to compile PIL, lxml etc).

Debian and derivatives like Ubuntu and Mint, Including c9.io
------------------------------------------------------------

.. code-block:: sh

    sudo apt-get update
    sudo apt-get install build-essential git python python-dev python-setuptools python-virtualenv python-pip
    sudo apt-get install libjpeg-dev libfreetype6 libfreetype6-dev
    sudo apt-get build-dep python-imaging
    sudo apt-get build-dep python-lxml


Fedora
-----------

.. code-block:: sh

    sudo yum groupinstall "Development Tools" "Development Libraries"
    sudo yum install git python python-devel python-setuptools python-virtualenv python-pip libjpeg-turbo-devel libpng-devel libxml2-devel libxslt-devel


Creating and Activating the virtualenv
===========================================

Navigate in a terminal to the directory you want the
environment created in (usually under your home directory). We'll name the
created environment ``oknesset``. 

Once in that directory:

.. code-block:: sh

    virtualenv oknesset

.. warning::

    In case you have both Python 2 and 3 installed, please make sure the virtualenv
    is created with Python 2. If that's not the case, pass the correct python
    executable to the virtualenv command. e.g:

    .. code-block:: sh

        virtualenv -p python2 oknesset

    To check which is the default interpreter virtualenv will use, run
    ``virtualenv -h`` and check in the output the default for `-p` flag.
    
We need to `activate` the virtual environment (it mainly modifies the paths so
that correct packages and bin directories will be found) each time we wish to
work on the code.

In Linux we'll source the activation script (to set env vars):

.. code-block:: sh

    cd oknesset/
    . bin/activate

Note the changed prompt which includes the virtualenv's name.


Getting the Source Code (a.k.a Cloning)
=========================================

Now we'll clone the forked repository into the virutalenv.  Make sure you're in
the `oknesset` directory and run::

    git clone https://github.com/your-username/Open-Knesset.git

Replace `your-username` with the username you've registered at git hub.

.. note::

    You can also clone with ssh keys, in that case follow the
    `github guide on ssh keys`_. Once you've done that, your clone command
    will look like::

        git@github.com:your-username/Open-Knesset.git

    For c9.io you will have to use ssh keys - you will need to add c9.io ssh key to your GitHub Profile's trusted keys.

.. _github guide on ssh keys: https://help.github.com/articles/generating-ssh-keys#platform-linux

.. note::
    If you have forked Open-Knesset in the past, make sure you have the latest version before proceeding to installation, by invoking::

        git remote add hasadna https://github.com/hasadna/Open-Knesset.git
        git pull hasadna master
        git push origin master

Installing requirements
=============================

Still in the terminal with the virtualenv activated, inside the *oknesset* directory,
run:

.. code-block:: sh

    pip install --upgrade pip
    pip install -r Open-Knesset/requirements.txt
    
And wait ...

Once done, proceed to :ref:`tests_develdb`.

Word Clouds
===================

Generating word clouds is a complex business and not part of the standard
enviornment. It requires matplotlib which is built on top of numpy and
requires some system wide installation.
To be able to generate word clouds you'll need to run the following commands:

.. code-block:: sh

    apt-get install libpng-dev libjpeg8-dev libfreetype6-dev python-tk
    pip install -r wc_requirments.txt

The clouds use the Alef font and if you don't have it you'll have to download
the zip_ an expand it in /usr/share/fonts/truetype/Alef/Alef-Regular.ttf

.. _zip: http://alef.hagilda.com/
