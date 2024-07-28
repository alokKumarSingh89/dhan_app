from fyers_apiv3.FyersWebsocket import data_ws

def connect_with_broker(script, token):
    def onmessage(message):
        if message["type"] == "sf":
            print(message["symbol"])
        print("Response:", message)
    def onerror(message):
        print("Error:", message)
    def onclose(message):
        print("Connection closed:", message)
    def onopen():
        data_type = "SymbolUpdate"
        # Subscribe to the specified symbols and data type
        symbols = [x["o_symbol"] for x in script]
        fyers.subscribe(symbols=symbols, data_type=data_type)

        # Keep the socket running to receive real-time data
        fyers.keep_running()
    
    fyers = data_ws.FyersDataSocket(
        access_token=token,       # Access token in the format "appid:accesstoken"
        log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
        litemode=True,                  # Lite mode disabled. Set to True if you want a lite response.
        write_to_file=False,              # Save response in a log file instead of printing it.
        reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
        on_connect=onopen,               # Callback function to subscribe to data upon connection.
        on_close=onclose,                # Callback function to handle WebSocket connection close events.
        on_error=onerror,                # Callback function to handle WebSocket errors.
        on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
    )
    fyers.connect()

