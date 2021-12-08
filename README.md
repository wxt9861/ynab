# ynab

YNAB component for Home Assistant  
This component will retreieve the following data from your YNAB budget

1. To be budgeted amount
2. Current month's budgeted amount
3. Current month's remaining balance of any specified category
4. Current balance of any specified account
5. Number of transactions needing approval
6. Number of uncleared transactions
7. Number of overspent categories

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
| `accounts` | `list`   | False    | None          | List of YNAB categories to include in the sensor. These are **CASE SENSITIVE**                       |

### Example default configuration.yaml

```yaml
ynab:
  api_key: <api_key_here>
```

### Example: configuration.yaml with options

```yaml
ynab:
  api_key: <api_key_here>
  name: "My YNAB Budget"
  budget: <budget_id_here>
  currency: "$"
  categories:
    - "HASS Budget"
    - "Vacation Budget"
  accounts:
    - "Savings Account"
```

### To enable debug

```yaml
logger:
  logs:
    custom_components.ynab: debug
```

### Generate YNAB API key / Get budget ID

API:

1. Log on to YNAB
2. Go to My Budget > My Account > Developer Settings
3. Click on New Token
4. Enter your password and click Generate
5. Copy the token that appears at the top of the page

Budget ID:  
The budget ID is the combination between the slashes after the URL <https://app.youneedabudget.com>
If you only have one budget, you can omit the the budget option, if you have multiple budgets pick a budget you want the sensor to report on. At this time only 1 budget is retrieved.
