# nowStudio App Upload - CLI

nowgg CLI is a command-line tool that enables you to upload your app builds to nowStudio.


## Prerequisites

+ Works with Python 3.8 and above.
+ App ID
    + Used to identify the App on nowStudio.
    + Your App ID can be found under the [App Details section](https://docs.now.gg/nowstudio/publish#app-details) of nowStudio.
+ Publisher token
    * Used to identify the publisher company.
    * Your Publisher token is available under the [Account Information](https://docs.now.gg/nowstudio/start-using-nowstudio#ac-info) section of nowStudio.

## Using nowgg CLI

Open any terminal on macOS or Windows.

#### Install nowgg CLI tool
```bash
  pip install nowgg
```
#### Initialize nowgg CLI
```bash
  nowgg init --token "<your_publisherToken_from_nowStudio>"
```

#### Upload App to App Library

```bash
  nowgg upload --app_id <your_app_id> --file_path "/directory/sample.apk" --apk_version <apk_version> --version_code <app_version_code>
```

#### Upload App to Test Track and Trigger Deployment
```bash
  nowgg upload --app_id <your_app_id> --file_path "/directory/sample.apk" --apk_version <apk_version> --version_code <app_version_code> --deploy
```

##### Note
- Each test track has a unique `app_id`, that you can use to create a draft release on that test track. For example, if your `app_id` is `1234`, the `app_id` for test track 1 would be `1234_t1`, 

- If you provide `1234` instead of `1234_t1` the app will be uploaded to the App library only.

- Adding `--deploy` triggers the deployment process on the specified test track, this will only work if you've given the `app_id` for a test track as per the above format.

Example for `--deploy`
```bash
  nowgg upload --app_id 1234_t1 --file_path "/directory/sample.apk" --apk_version 1.0 --version_code 342 --deploy
```


## For Help

```bash
  nowgg -h
  nowgg init -h
  nowgg upload -h
```  

**Note**: Your app will be uploaded to the App Library within nowStudio.

## Important Information

+ While running the nowgg command, If you receive a `‘command not recognized’` error, consider adding` <python directory>\<Scripts>  `to your PATH.
+ If you receive any  `'permission-related errors'`, you should run the commands as an Administrator.