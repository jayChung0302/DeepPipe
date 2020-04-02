# DeepPipe server

## Prerequisites

.NET Core 3.1 SDK

## Configuration

```json
{
    "DeepPipe":{
        "Python":"python",
        "Command":"inout.py"
    }
}
```

## Run

### Bash

```bash
git clone https://github.com/jayChung0302/DeepPipe
mv DeepPipe
dotnet run --project server/src/DpWeb/DpWeb.csproj --DeepPipe:Python python3 --DeepPipe:Command $(pwd)/python_demo/inout.py
```
