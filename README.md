# AI-Hearts
前進福岡之戰


# Setup Environment

Virtualenv create new env

``` sh
virtualenv -p python3.6 --no-site-packages ~/.virtualenvs/ai_hearts/
```

Activate the env

``` sh
. ~/.virtualenvs/ai_hearts/bin/activate
```

Install requirement.txt

``` sh 
pip install -r requirement.txt
```

# Implement rule-based bot
The example is at *rule_bot.py*, and you can simply implement the function `declare_action` to fulfill the Hearts SDK. The `declare_action` uses the `GameInfo` to determine what action should be taken, in addition, the `declare_action` will also apply to the **gym** environment.
