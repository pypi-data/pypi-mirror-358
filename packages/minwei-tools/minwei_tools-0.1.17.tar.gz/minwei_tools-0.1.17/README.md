# minwei_tools

### This tools contain 3 major function

1. Dotter : Display animated text on screen during long missions
2. re_result : A Rust-like approach to error handling
3. server : A file transfer server 
4. us_doc : A `uv` doc generator

# Install

```bash
pip install minwei_tools
```

# Usage

* ## File Transfer server

    ```python
    python -m minwei_tools.server -p {port} -h {host}
    ```

    ![alt text](file_server.gif)

* ## Dotter

    An example of dotter, DotStyle have many style can use.

    ```python
    from minwei_tools import Dotter
    from minwei_tools import DotStyle
    from time import sleep

    rand_style = DotStyle.random()

    with Dotter(message="[*] Normal speed", cycle=rand_style, delay=0.25, show_timer=0) as d:
        d.insert_message("This is a test message 1")
        sleep(1)
        d.insert_message("This is a test message 2")
        sleep(1)
        d.insert_message("This is a test message 3")
        sleep(1)
        d.update_message("[*] Fast spin", delay=0.05)
        sleep(1)
        d.insert_message("This is a test message 4")
        sleep(1)
        d.insert_message("This is a test message 5")
        sleep(1)        
        d.insert_message("This is a test message 6")
        d.update_message("[*] Slow spin", delay=1)
        for i in range(7, 80):
            d.insert_message(f"This is another message {i}", max_str = 10, prefix = "*")
            sleep(0.05)
        d.update_message("[*] Longer msg", delay=0.5)
        for i in range(80, 250):
            d.insert_message(f"This is another message {i}", max_str = 20, prefix = f"🚀{cm.Style.RESET_ALL}{cm.Style.BRIGHT}")
            sleep(0.01)       
        d.update_message("[*] Short msg", delay=0.5)
            
        for i in range(250, 500):
            d.insert_message(f"This is another message {i}", max_str = 3, prefix = f"{cm.Style.RESET_ALL}{cm.Style.BRIGHT}🚀{cm.Style.RESET_ALL}{cm.Style.DIM}")
            sleep(0.01)                           
    ```

    ![alt text](loading.gif)

    Also support an `async` dotter

    ```python
    from time import sleep
    import asyncio

    from minwei_tools import AsyncDotter

    async def main():
        async with AsyncDotter("Thinking", show_timer=True, delay=0.1):
            await asyncio.sleep(120)

    asyncio.run(main())
    ```

* ## rs_result

    ```python
    from minwei_tools.rs_result import Result, Ok, Err

    def devide(a: int, b: int) -> Result[int, str]:
        if b == 0:
            return Err("Division by zero error")
        return Ok(a // b)

    """
    >>> result : Result[int, str] = devide(10, 0)
    >>> result.is_ok()
    False
    >>> result.is_err()
    >>> result : Result[int, str] = devide(10, 2)
    >>> result.is_ok()
    True
    >>> result.unwrap()
    5
    """

    result : Result[int, str] = devide(10, 0)
    match result:
        case Ok(value):
            print(f"Result: {value}")
        case Err(value):
            print(f"Error: {value}")
            
    result : Result[int, str] = devide(10, 2)
    match result:
        case Ok(value):
            print(f"Result: {value}")
        case Err(value):
            print(f"Error: {value}")
    ```

* ## uv doc
    ```bash
    python -m minwei_tools.uv_doc -p {PROJECT_NAME}
    ```

    ![alt text](uv_doc.gif)


    ```
    -h, --help            show this help message and exit
    -p PROJECT_NAME, --project_name PROJECT_NAME
                            Name of the project. Defaults to the current directory name.
    -o OUTPUT, --output OUTPUT
                            Output file name. Defaults to README.md.
    -d DIRECTORY, --directory DIRECTORY
                            Directory to scan. Defaults to the current working directory.
    ```