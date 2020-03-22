# Getting Started

## Invite Cosmos bot

> **Inviting Cosmos bot with default administrator permissions ensures smooth working of all of its features and plugins without any unexpected errors.**

[Invite Cosmos to your server](https://discordapp.com/oauth2/authorize?client_id=390176338729893889&scope=bot&permissions=8) or use the following invite URL with administrator permissions.

`https://discordapp.com/oauth2/authorize?client_id=390176338729893889&scope=bot&permissions=8`

## Self Hosting

If you're willing to run your own custom instance of Cosmos bot, you can easily do so by getting its source code and performing a quick setup by installing Python and other dependencies.

### Installing Python

Cosmos bot requires at least Python 3.8 or more to run. Depending on the operating system you're running, you can get it from their [official website](https://www.python.org/downloads/).   
If you're running Linux or any Debian based system, you can simply get it by running following commands:

```bash
$ sudo su
$ apt install python3.8
# Install optional dependencies for voice support.
$ apt install libffi-dev libnacl-dev python3-dev
```

### Getting the source

Get the latest source of Cosmos bot from the [Github repository](https://github.com/thec0sm0s/cosmos-discord-bot.git) using Git or just get the zip file and then extract on your local file system.  
To get the welcome banners and other image based features working, get the [Image Processor source ](https://github.com/thec0sm0s/image-processor.git)and include it in the main source code of the Cosmos bot.

```bash
$ git clone https://github.com/thec0sm0s/cosmos-discord-bot.git
# Get the Image Processor.
$ git clone https://github.com/thec0sm0s/image-processor.git
```

### Installing dependencies

#### MongoDB

Cosmos bot uses [MongoDB](https://www.mongodb.com/) to store all of the required data. You will be required to setup the database server. You may either use the [MogoDB cloud services](https://www.mongodb.com/cloud/atlas) or run it on your own local server. Check its guide on [installing MongoDB](https://docs.mongodb.com/manual/installation/) on your local machine.

#### Python Requirements

Requirements for Cosmos bot and Image Processor can be installing using following command. Just make sure you're in root directory of the Cosmos' source code.

```bash
$ python3.8 -m pip install -r cosmos-discord-bot/requirements.txt
$ python3.8 -m pip install -r image-processor/requirements.txt
```

### Final Configuration

The final step is to do the important configuration in the different config files which resides under the `cosmos-discord-bot/cfg/` directory. You can check all of the configs files and make changes as you wish and whatever the way you want in customizing the bot.

#### Core Configs

Prepare and check all of the config files except as required. Cosmos bot uses several emotes for visual better visual appearance internally which were previously added in different servers. If you want to keep using the default emotes added on our emote servers, you will have to get your bot added to our emote servers by asking for it in [our community](https://discord.gg/7ChSGn4).  
The other option is to manually create your own emote servers and add all of the emotes which are used by Cosmos bot and put their IDs in the `emotes.yaml` file. All of the emotes internally used by Cosmos bot are given below.

{% hint style="info" %}
Emotes are given in format `:name_of_emote:. Animated emotes are prefixed with a.`
{% endhint %}

* **misc**

`a:square_load:` `a:yellow_square_load:` `:next:` `:prev:` `:close:` `:forward:` `:backward:` `:return_:` `:check:` `:timer:` `:coins:`

* **foods**

`:tomato_garlic:` `:doughnut:` `:watermelon:` `:pizza:` `:fallen_cone:` `:strawberry:` `:cherry:` `:grapes:` `:eggplant:` `:chili:` `:mushroom:` `:popcorn:` `:lollipop:` `:pancake:` `:honey:` `:orange:` `:jam:` `:cheese:` `:burger:` `:icecream:`

#### Theme Configs

Not important but config files inside this directory or category determines the default appearance of the Cosmos bot.

### Starting the bot

Use Python to run the `run.py` file to start the Cosmos bot. In separate process run `wsgi.py` file to start the Image Processor server and make sure the port `5000` is free which is used as default.  
On Linux machines, you can use the following commands.

```bash
# Terminal 1
$ python3.8 cosmos-discord-bot/run.py
```

```bash
# Terminal 2
$ cd image-processor
$ gunicorn -b 127.0.0.1:5000 "app:create_app()"
```

{% hint style="info" %}
You can also use services or containers to run the Cosmos bot and Image Processor server.
{% endhint %}

