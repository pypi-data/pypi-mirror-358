# nonebot_plugin_awsmgmt

一个用于 AWS 管理的 NoneBot2 插件。

## 使用方法

---
### EC2
- `/ec2_start [target]`
- `/ec2_stop [target]`
- `/ec2_reboot [target]`
- `/ec2_status [target]`

**Target (目标):**
- `tag:Key:Value`:  例如 `tag:Project:MyProject`
- `id:i-xxxx`: 例如 `id:i-0fd0acc80b595ac71`

如果未提供 `target`，插件将使用您在配置中设置的 `aws_default_target_tag`（如果已设置）。

---
### Lightsail
- `/lightsail_list`
- `/lightsail_start <实例名称>`
- `/lightsail_stop <实例名称>`

---
### Cost Explorer (成本管理器)
- `/aws_cost today` (今日成本)
- `/aws_cost month` (本月成本)
- `/aws_cost month by_service` (按服务划分的本月成本)

## 安装

1.  **安装插件**

    ```bash
    pip install nonebot-plugin-awsmgmt
    ```

2.  **在 NoneBot2 项目中加载插件**

    在 `bot.py` 或 `pyproject.toml` 中添加 `nonebot_plugin_awsmgmt` 到插件列表。

    例如，在 `pyproject.toml` 中：

    ```toml
    [tool.nonebot]
    plugins = ["nonebot_plugin_awsmgmt"]
    ```

3.  **配置 AWS 凭证**

    在您的 NoneBot2 项目的 `.env` 文件中配置您的 AWS 访问密钥和秘密访问密钥：

    ```
    AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
    AWS_REGION_NAME=your-aws-region # 例如: us-east-1
    ```

## AWS 侧配置

为了使插件能够管理您的 AWS 资源，您需要在 AWS IAM 中创建一个具有适当权限的用户。

### 1. 创建 IAM Policy

创建一个新的 IAM Policy，并粘贴以下 JSON 内容。您可以根据需要修改此策略以限制权限。

**Policy JSON (`aws-policy.json`):**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:RebootInstances"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/ManagedBy": "nonebot-plugin-awsmgmt"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "lightsail:GetInstances",
                "lightsail:GetInstance",
                "lightsail:StartInstance",
                "lightsail:StopInstance"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage"
            ],
            "Resource": "*"
        }
    ]
}
```

**步骤：**

1.  登录 AWS 管理控制台。
2.  导航到 IAM 服务。
3.  在左侧导航栏中选择 **Policies**。
4.  点击 **Create policy**。
5.  选择 **JSON** 选项卡，并粘贴上述 Policy JSON 内容。
6.  点击 **Next: Tags**，然后点击 **Next: Review**。
7.  为策略命名（例如：`NoneBotAWSPolicy`），并添加描述。
8.  点击 **Create policy**。

### 2. 创建 IAM 用户并附加策略

创建一个新的 IAM 用户，并为其提供编程访问权限，然后附加您刚刚创建的策略。

**步骤：**

1.  在 IAM 服务中，选择左侧导航栏中的 **Users**。
2.  点击 **Add user**。
3.  输入用户名（例如：`nonebot-aws-user`）。
4.  在 **Select AWS access type** 部分，勾选 **Programmatic access**。
5.  点击 **Next: Permissions**。
6.  选择 **Attach existing policies directly**。
7.  搜索并选择您刚刚创建的策略（例如：`NoneBotAWSPolicy`）。
8.  点击 **Next: Tags**，然后点击 **Next: Review**。
9.  点击 **Create user**。
10. **重要：** 记录下生成的 **Access key ID** 和 **Secret access key**。这些将用于配置 NoneBot2 插件。这些凭证只显示一次，请务必妥善保管。