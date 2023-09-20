# ynab

YNAB component for Home Assistant
This component will retreieve the following data from your YNAB budget

1. To be budgeted amount
2. Current month's budgeted amount
3. Current month's remaining balance of any specified category
4. Current month's budgeted amount of any specific category
5. Current balance of any specified account
6. Number of transactions needing approval
7. Number of uncleared transactions
8. Number of overspent categories

To keep api usage low, the sensor updates every 5 minutes.

## Installation

### HACS

1. Open HACS > Settings
2. In ADD CUSTOM REPOSITORY box paste this git's URL <https://github.com/wxt9861/ynab> and select type Integration
3. Click INSTALL
4. Make necessary modifications to your configuration.yaml
5. Restart Home Assistant

### Manual install

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ynab.
4. Download all the files from the custom_components/ynab/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Add ynab: to your HA configuration (see examples below)
7. Restart Home Assistant

## Configuration options

| Key          | Type     | Required | Default     | Description                                                                                          |
| ------------ | -------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------- |
| `api_key`    | `string` | `True`   | None        | YNAB API key (see instructions below)                                                                |
| `name`       | `string` | False    | sensor.ynab | Custom name for the sensor                                                                           |
| `budget`     | `string` | False    | last-used   | Budget ID to use if you have multiple budgets. If none specified, your last used budget will be used |
| `currency`   | `string` | False    | \$          | Currency to use as unit of measurement                                                               |
| `categories` | `list`   | False    | None        | List of YNAB categories to include in the sensor. These are **CASE SENSITIVE**                       |
| `accounts` | `list`   | False    | None          | List of YNAB accounts to include in the sensor. These are **CASE SENSITIVE**                       |

### To enable debug

```yaml
logger:
  logs:
    custom_components.ynab: debug
```

### Generate YNAB API key

API:

1. Log on to YNAB
2. Go to My Budget > My Account > Developer Settings
3. Click on New Token
4. Enter your password and click Generate
5. Copy the token that appears at the top of the page

### Setup the integration

1. Navigate to Settings -> Devices & Services on your Home Assistant instance
2. Select "Add Integration" in the bottom right hand corner
3. Search for and select "ynab" from the list
4. Enter your API key from the previous step into the "API Key" field and click submit
5. Your API key will be validated and your budgets retrieved.  Select the budget you want to use from the list
6. Select one or more categories to sync then click "Submit", or if you don't want to sync any categories just click "Submit"
7. Select one or more accounts to sync then click "Submit", or if you don't want to sync any accounts just click "Submit"

The budget is now setup and will start updating automatically.  You can go through the same process to add multiple budgets all of which will be kept updated.