# FAQ

## Why tydom2mqtt?
Deltadore doesn't provide an official solution to make their hardware compatible with home automation solutions (Home-assistant...)

## How to reset my tydom password?
In october 2021, Deltadore has released a new version of its Tydom app (v4+) preventing to set or reset the Tydom password.

To set/reset your password, better download the previous version (v3+) which still allows to do it ([Aptoide link](https://tydom.fr.aptoide.com/app?store_name=aptoide-web&app_id=58618221)).

## How to prevent my tydom from communicating with Deltadore servers?
If you're concerned about your privacy, you can perform the following actions:
1. Configure you router to forbid your Tydom hub to access internet
2. Find your tydom local IP address and use it as `TYDOM_IP` value

## Why alarm motion sensor activity isn't reported?
- Alarm motion sensor activity isn't reported but when the alarm is fired then you get a cdata message so you can get the info (only when alarm is armed, pending and triggered).
