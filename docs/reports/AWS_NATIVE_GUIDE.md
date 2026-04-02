# AWS Native Deployment Guide

This guide explains how to run Bedrock Copilot in different AWS environments using native credentials.

## 1. Local Development (with Profiles)

If you use AWS SSO or named profiles:

```bash
export AWS_PROFILE=my-svc-account
python src/main.py
```

## 2. EC2 Instance Deployment

1. Create an IAM Role with `bedrock_copilot_policy.json`
2. Attach the role to your EC2 instance.
3. Run the app without any environment variables:

```bash
python src/main.py
```J
copilot will automatically detect the instance profile and use it.

## 3. AWS SSO Support

The app fully supports AWS SSO via the native boto3 credential chain. Ensure your app-config uses the region defined in your SSO profile.

## 4. Security Best Practices

- Never hardcode CKA/SAK in the app.
- Prefer IAM Roles for any cloud deployment.
- Use the provided LOP json policy to limit exposure.
