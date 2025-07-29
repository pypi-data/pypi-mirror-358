# evemap

Map plugin for [AllianceAuth](https://gitlab.com/allianceauth/allianceauth).

> This is a proof-of-concept that is a work-in-progress.

## Features

- Pan + Zoom
- - Scroll to zoom
- - Shift + Drag to zoom to box
- - Alt + Shift + Drag to rotate

### Regions View
- Dynamic styles based on zoom level
- - Far: Regions + Connections
- - Close: System names + Gate Network
- Click System Point/Name for info pane
- Click Region Name to open Single Region View

### Region View
Isolate and view a region
- Click Plan View (top left) to open Region Plan View

### Region Plan View
Whilst maintaining the connections of the Stargate Network, re-organises the layout in a logical view.

## Installation

### Step 1 - Pre-Requisites

Evemap is an App for Alliance Auth, Please make sure you have this installed. Evemap is not a standalone Django Application.

### Step 2 - Install app

pip install evemap

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

```python
INSTALLED_APPS += [
	'eveuniverse',
	'evemap',
...
```

### Step 4 - Maintain Alliance Auth

- Run migrations `python manage.py migrate`
- Gather your static-files `python manage.py collectstatic`
- Restart Alliance Auth

# Screenshots

## Universe
![Universe](https://i.imgur.com/y6euNrj.png)

## Universe Close
![Universe Close](https://i.imgur.com/4MBfWVP.png)

## Single Region View
![Single Region](https://i.imgur.com/Ur2WQse.png)

## Single Region Plan View
![Single Region Plan](https://i.imgur.com/7rPaFsx.png)

## Single Region Plan View (with info overlay)
![Single Region Plan Info](https://i.imgur.com/RCg8SUM.png)
