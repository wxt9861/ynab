# Configuration options

| Key          | Type     | Required | Default     | Description                                                                                          |
| ------------ | -------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------- |
| `api_key`    | `string` | `True`   | None        | YNAB API key (see insturctions below)                                                                |
| `name`       | `string` | False    | sensor.ynab | Custom name for the sensor                                                                           |
| `budget`     | `string` | False    | last-used   | Budget ID to use if you have multiple budgets. If none specified, your last used budget will be used |
| `currency`   | `string` | False    | \$          | Currency to use as unit of measurement                                                               |
| `categories` | `list`   | False    | None        | List of YNAB categories to include in the sensor. These are **CASE SENSATIVE**                       |

## Example default configuration.yaml

```yaml
ynab:
  api_key: <api_key_here>
```

## Example: configuration.yaml with options

```yaml
ynab:
  api_key: <api_key_here>
  name: "My YNAB Budget"
  budget: <budget_id_here>
  currency: "$"
  categories:
    - "HASS Budget"
    - "Vacation Budget"
```

## Generate YNAB API key / Get budget ID

API:

1. Log on to YNAB
2. Go to My Budget > My Account > Developer Settings
3. Click on New Token
4. Enter your password and click Generate
5. Copy the token that appears at the top of the page

Bidget ID:

The budget ID is the combination between the slahses after the URL <https://app.youneedabudget.com>
If you only have one budget, you can leave the budget option at default, if you have multiple budgets pick a budget you want the sensor to report on. At this time data from only 1 budget is retrieved.
