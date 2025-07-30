#!/usr/bin/env python3
"""
Tool Handlers for Binance MCP Server
"""

from typing import Any, Dict

from .cache import TickerCache
from .client import BinanceClient
from .config import BinanceConfig


class ToolHandler:
    """Handles tool execution for the MCP server"""
    
    def __init__(self, config: BinanceConfig, ticker_cache: TickerCache):
        self.config = config
        self.ticker_cache = ticker_cache
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""
        
        async with BinanceClient(self.config) as client:
            
            # Account Information Tools
            if name == "get_account_info":
                return await client._make_request("GET", "/fapi/v2/account", security_type="USER_DATA")
            elif name == "get_balance":
                return await client._make_request("GET", "/fapi/v2/balance", security_type="USER_DATA")
            elif name == "get_position_info":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v2/positionRisk", params, "USER_DATA")
            elif name == "get_position_mode":
                return await client._make_request("GET", "/fapi/v1/positionSide/dual", security_type="USER_DATA")
            elif name == "get_commission_rate":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("GET", "/fapi/v1/commissionRate", params, "USER_DATA")
            
            # Risk Management Tools
            elif name == "get_adl_quantile":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/adlQuantile", params, "USER_DATA")
            elif name == "get_leverage_brackets":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/leverageBracket", params, "USER_DATA")
            elif name == "get_force_orders":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/forceOrders", params, "USER_DATA")
            elif name == "get_position_margin_history":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/positionMargin/history", params, "USER_DATA")
            
            # Order Management Tools
            elif name == "place_order":
                return await self._handle_place_order(client, arguments)
            elif name == "place_multiple_orders":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("POST", "/fapi/v1/batchOrders", params, "TRADE")
            elif name == "cancel_order":
                params = {"symbol": arguments["symbol"], "orderId": arguments["order_id"]}
                return await client._make_request("DELETE", "/fapi/v1/order", params, "TRADE")
            elif name == "cancel_multiple_orders":
                params = {
                    "symbol": arguments["symbol"],
                    "orderIdList": arguments["order_id_list"]
                }
                return await client._make_request("DELETE", "/fapi/v1/batchOrders", params, "TRADE")
            elif name == "cancel_all_orders":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("DELETE", "/fapi/v1/allOpenOrders", params, "TRADE")
            elif name == "auto_cancel_all_orders":
                params = {
                    "symbol": arguments["symbol"],
                    "countdownTime": arguments["countdown_time"]
                }
                return await client._make_request("POST", "/fapi/v1/countdownCancelAll", params, "TRADE")
            
            # Order Query Tools
            elif name == "get_open_order":
                params = {"symbol": arguments["symbol"], "orderId": arguments["order_id"]}
                return await client._make_request("GET", "/fapi/v1/openOrder", params, "USER_DATA")
            elif name == "get_open_orders":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("GET", "/fapi/v1/openOrders", params, "USER_DATA")
            elif name == "get_all_orders":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/allOrders", params, "USER_DATA")
            elif name == "query_order":
                params = {"symbol": arguments["symbol"], "orderId": arguments["order_id"]}
                return await client._make_request("GET", "/fapi/v1/order", params, "USER_DATA")
            
            # Position Management Tools
            elif name == "close_position":
                return await self._handle_close_position(client, arguments)
            elif name == "modify_order":
                return await self._handle_modify_order(client, arguments)
            elif name == "add_tp_sl_to_position":
                return await self._handle_add_tp_sl(client, arguments)
            elif name == "place_bracket_order":
                return await self._handle_bracket_order(client, arguments)
            
            # Trading Configuration Tools
            elif name == "change_leverage":
                params = {"symbol": arguments["symbol"], "leverage": arguments["leverage"]}
                return await client._make_request("POST", "/fapi/v1/leverage", params, "TRADE")
            elif name == "change_margin_type":
                params = {"symbol": arguments["symbol"], "marginType": arguments["margin_type"]}
                return await client._make_request("POST", "/fapi/v1/marginType", params, "TRADE")
            elif name == "change_position_mode":
                params = {"dualSidePosition": arguments["dual_side"]}
                return await client._make_request("POST", "/fapi/v1/positionSide/dual", params, "TRADE")
            elif name == "modify_position_margin":
                params = {
                    "symbol": arguments["symbol"],
                    "amount": arguments["amount"],
                    "positionSide": arguments["position_side"],
                    "type": arguments["margin_type"]
                }
                return await client._make_request("POST", "/fapi/v1/positionMargin", params, "TRADE")
            
            # Market Data Tools
            elif name == "get_exchange_info":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/exchangeInfo", params)
            elif name == "get_book_ticker":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/ticker/bookTicker", params)
            elif name == "get_price_ticker":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/ticker/price", params)
            elif name == "get_24hr_ticker":
                if "symbol" in arguments:
                    # Single symbol from cache
                    symbol_data = self.ticker_cache.get_symbol_data(arguments["symbol"])
                    if symbol_data:
                        return symbol_data
                    else:
                        # Fallback to API if not in cache
                        params = {"symbol": arguments["symbol"]}
                        return await client._make_request("GET", "/fapi/v1/ticker/24hr", params)
                else:
                    # All symbols from cache
                    return self.ticker_cache.data
            elif name == "get_top_gainers_losers":
                return self._handle_top_gainers_losers(arguments)
            elif name == "get_market_overview":
                return self._handle_market_overview(arguments)
            elif name == "get_order_book":
                params = {
                    "symbol": arguments["symbol"],
                    "limit": arguments["limit"]
                }
                return await client._make_request("GET", "/fapi/v1/depth", params)
            elif name == "get_klines":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/klines", params)
            elif name == "get_mark_price":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/premiumIndex", params)
            elif name == "get_aggregate_trades":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/aggTrades", params)
            elif name == "get_funding_rate_history":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/fundingRate", params)
            elif name == "get_taker_buy_sell_volume":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/futures/data/takerlongshortRatio", params)
            
            # Trading History Tools
            elif name == "get_account_trades":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/userTrades", params, "USER_DATA")
            elif name == "get_income_history":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/income", params, "USER_DATA")
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_place_order(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle place_order tool
    
    Places an order with optional take-profit (TP) and stop-loss (SL) orders.
    When TP and/or SL parameters are provided, this functions like a bracket order.
    
    Args:
        client: BinanceClient instance
        arguments: Dictionary containing order parameters
            Standard order parameters:
            - symbol: Trading pair symbol (e.g., "BTCUSDT")
            - side: Order side ("BUY" or "SELL")
            - type: Order type ("LIMIT", "MARKET", "STOP", "STOP_MARKET", "TAKE_PROFIT", 
              "TAKE_PROFIT_MARKET", "TRAILING_STOP_MARKET")
            - quantity: Order quantity
            - price: Price for LIMIT/STOP/TAKE_PROFIT orders
            - stopPrice: Trigger price for STOP/STOP_MARKET/TAKE_PROFIT/TAKE_PROFIT_MARKET orders
            - timeInForce: Time in force for LIMIT orders (default: "GTC")
            - positionSide: Position side for hedge mode ("LONG", "SHORT", or "BOTH")
            - callbackRate: Required for TRAILING_STOP_MARKET orders
            - activationPrice: Optional for TRAILING_STOP_MARKET orders
            
            Risk management parameters (optional):
            - take_profit_price: Price for take-profit order
            - stop_loss_price: Price for stop-loss order
            - tp_type: Take-profit order type ("LIMIT" or "MARKET"), default is "LIMIT"
            - sl_type: Stop-loss order type ("LIMIT" or "MARKET"), default is "LIMIT"
            - leverage: Leverage to set before placing orders
            
    Returns:
        Dictionary containing the results of all placed orders
    """
    # Extract risk management parameters if present
    take_profit_price = arguments.pop("take_profit_price", None)
    stop_loss_price = arguments.pop("stop_loss_price", None)
    tp_type = arguments.pop("tp_type", "LIMIT")
    sl_type = arguments.pop("sl_type", "LIMIT")
    leverage = arguments.pop("leverage", None)
    
    # Check if this is a bracket order (has TP or SL)
    is_bracket_order = take_profit_price is not None or stop_loss_price is not None
    
    # Filter out precision parameters and pass through all other parameters directly
    params = {k: v for k, v in arguments.items() if v is not None and k not in ["quantity_precision", "price_precision"]}
    
    # Handle backward compatibility for order_type parameter
    if "order_type" in params:
        params["type"] = params.pop("order_type")
    
    # Check if type parameter is present
    if "type" not in params:
        raise ValueError("Missing required parameter 'type'. Please specify the order type (e.g., 'MARKET', 'LIMIT', 'STOP', etc.)")
    
    # Validate mandatory parameters based on order type
    order_type = params.get("type")
    if order_type == "LIMIT":
        required_params = ["timeInForce", "quantity", "price"]
        missing = [p for p in required_params if p not in params]
        if missing:
            raise ValueError(f"LIMIT order missing required parameters: {missing}")
    elif order_type == "MARKET":
        if "quantity" not in params:
            raise ValueError("MARKET order missing required parameter: quantity")
    elif order_type in ["STOP", "TAKE_PROFIT"]:
        required_params = ["quantity", "price", "stopPrice"]
        missing = [p for p in required_params if p not in params]
        if missing:
            raise ValueError(f"{order_type} order missing required parameters: {missing}")
    elif order_type in ["STOP_MARKET", "TAKE_PROFIT_MARKET"]:
        if "stopPrice" not in params:
            raise ValueError(f"{order_type} order missing required parameter: stopPrice")
    elif order_type == "TRAILING_STOP_MARKET":
        if "callbackRate" not in params:
            raise ValueError("TRAILING_STOP_MARKET order missing required parameter: callbackRate")
    
    # Set leverage if provided
    if leverage:
        try:
            await client._make_request(
                "POST", 
                "/fapi/v1/leverage", 
                {"symbol": params["symbol"], "leverage": leverage},
                "USER_DATA"
            )
        except Exception as e:
            print(f"Warning: Failed to set leverage: {e}")
    
    # If not a bracket order, just place the single order and return
    if not is_bracket_order:
        return await client._make_request("POST", "/fapi/v1/order", params, "TRADE")
    
    # For bracket orders, we need to place the entry order first, then TP and SL
    result = {
        "order": {
            "symbol": params["symbol"],
            "side": params["side"],
            "type": params["type"],
            "orders": {}
        }
    }
    
    try:
        # 1. Place entry order
        entry_order = await client._make_request("POST", "/fapi/v1/order", params, "TRADE")
        result["order"]["orders"]["entry"] = entry_order
        
        # Determine opposite side for TP and SL orders
        side = params["side"]
        opposite_side = "SELL" if side == "BUY" else "BUY"
        position_side = params.get("positionSide", "BOTH")
        symbol = params["symbol"]
        quantity = params["quantity"]
        time_in_force = params.get("timeInForce", "GTC")
        
        # 2. Place take-profit order if specified
        if take_profit_price:
            tp_order_type = "TAKE_PROFIT" if tp_type == "LIMIT" else "TAKE_PROFIT_MARKET"
            tp_params = {
                "symbol": symbol,
                "side": opposite_side,
                "positionSide": position_side,
                "quantity": quantity,
                "type": tp_order_type,
                "stopPrice": take_profit_price,
                "reduceOnly": "true"  # Ensure it only reduces the position
            }
            
            # Add price and timeInForce only for LIMIT take-profit orders
            if tp_type == "LIMIT":
                tp_params["price"] = take_profit_price
                tp_params["timeInForce"] = time_in_force
            
            tp_order = await client._make_request(
                "POST", 
                "/fapi/v1/order", 
                tp_params,
                "TRADE"
            )
            
            result["order"]["orders"]["take_profit"] = tp_order
        
        # 3. Place stop-loss order if specified
        if stop_loss_price:
            sl_order_type = "STOP" if sl_type == "LIMIT" else "STOP_MARKET"
            sl_params = {
                "symbol": symbol,
                "side": opposite_side,
                "positionSide": position_side,
                "quantity": quantity,
                "type": sl_order_type,
                "stopPrice": stop_loss_price,
                "reduceOnly": "true"  # Ensure it only reduces the position
            }
            
            # Add price and timeInForce only for LIMIT stop-loss orders
            if sl_type == "LIMIT":
                sl_params["price"] = stop_loss_price
                sl_params["timeInForce"] = time_in_force
            
            sl_order = await client._make_request(
                "POST", 
                "/fapi/v1/order", 
                sl_params,
                "TRADE"
            )
            
            result["order"]["orders"]["stop_loss"] = sl_order
        
        return result
        
    except Exception as e:
        # If any order fails, attempt to cancel any successful orders
        if "orders" in result["order"]:
            for order_type, order in result["order"]["orders"].items():
                if "orderId" in order:
                    try:
                        await client._make_request(
                            "DELETE", 
                            "/fapi/v1/order", 
                            {"symbol": symbol, "orderId": order["orderId"]},
                            "TRADE"
                        )
                    except Exception as cancel_error:
                        print(f"Failed to cancel {order_type} order: {cancel_error}")
        
        # Re-raise the original exception
        raise ValueError(f"Failed to place order: {str(e)}")
    
    async def _handle_close_position(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle close_position tool"""
        symbol = arguments["symbol"]
        position_side = arguments.get("position_side", "BOTH")
        quantity = arguments.get("quantity")
{{ ... }}
        close_all = arguments.get("close_all", False)
        
        # First, get current position to determine the side and quantity to close
        position_params = {"symbol": symbol}
        positions = await client._make_request("GET", "/fapi/v2/positionRisk", position_params, "USER_DATA")
        
        # Find the position to close
        position_to_close = None
        for pos in positions:
            if pos["symbol"] == symbol and float(pos["positionAmt"]) != 0:
                if position_side == "BOTH" or pos["positionSide"] == position_side:
                    position_to_close = pos
                    break
        
        if not position_to_close:
            raise ValueError(f"No open position found for {symbol} with position side {position_side}")
        
        position_amt = float(position_to_close["positionAmt"])
        current_position_side = position_to_close["positionSide"]
        
        # Determine order side (opposite of position)
        if position_amt > 0:  # Long position
            order_side = "SELL"
        else:  # Short position
            order_side = "BUY"
            position_amt = abs(position_amt)  # Make positive for order quantity
        
        # Determine quantity to close
        if close_all:
            # Use closePosition parameter to close entire position
            order_params = {
                "symbol": symbol,
                "side": order_side,
                "type": "MARKET",
                "closePosition": "true"
            }
            if current_position_side != "BOTH":
                order_params["positionSide"] = current_position_side
        else:
            # Close specific quantity or entire position
            close_quantity = quantity if quantity else position_amt
            order_params = {
                "symbol": symbol,
                "side": order_side,
                "type": "MARKET",
                "quantity": close_quantity
            }
            if current_position_side != "BOTH":
                order_params["positionSide"] = current_position_side
        
        return await client._make_request("POST", "/fapi/v1/order", order_params, "TRADE")
    
    async def _handle_modify_order(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle modify_order tool"""
        params = {
            "symbol": arguments["symbol"],
            "orderId": arguments["order_id"],
            "side": arguments["side"],
            "quantity": arguments["quantity"],
            "price": arguments["price"]
        }
        if "priceMatch" in arguments:
            params["priceMatch"] = arguments["priceMatch"]
        return await client._make_request("PUT", "/fapi/v1/order", params, "TRADE")
    
    async def _handle_add_tp_sl(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_tp_sl_to_position tool"""
        # Implementation for adding TP/SL would go here
        # This is a complex operation that requires getting current position and placing conditional orders
        raise NotImplementedError("add_tp_sl_to_position handler not fully implemented yet")
    
    async def _handle_bracket_order(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle place_bracket_order tool
        
        Places a bracket order which consists of:
        1. An entry order (main order)
        2. A take-profit (TP) order
        3. A stop-loss (SL) order
        
        Both TP and SL orders are placed with reduceOnly=True to ensure they only reduce the position.
        
        Args:
            client: BinanceClient instance
            arguments: Dictionary containing order parameters
                - symbol: Trading pair symbol (e.g., "BTCUSDT")
                - side: Order side ("BUY" or "SELL")
                - quantity: Order quantity
                - entry_type: Type of entry order ("LIMIT", "MARKET", "STOP", "STOP_MARKET", 
                  "TAKE_PROFIT", "TAKE_PROFIT_MARKET", "TRAILING_STOP_MARKET")
                - entry_price: Price for LIMIT/STOP/TAKE_PROFIT entry orders
                - stop_price: Trigger price for STOP/STOP_MARKET/TAKE_PROFIT/TAKE_PROFIT_MARKET orders
                - callback_rate: Required for TRAILING_STOP_MARKET orders (e.g., 0.8 for 0.8%)
                - activation_price: Optional for TRAILING_STOP_MARKET orders
                - take_profit_price: Price for take-profit order
                - stop_loss_price: Price for stop-loss order
                - position_side: Optional position side for hedge mode ("LONG", "SHORT", or "BOTH")
                - time_in_force: Optional time in force for LIMIT orders (default: "GTC")
                - leverage: Optional leverage to set before placing orders
                - tp_type: Optional take-profit order type ("LIMIT", "MARKET"), default is "LIMIT"
                - sl_type: Optional stop-loss order type ("LIMIT", "MARKET"), default is "LIMIT"
                
        Returns:
            Dictionary containing the results of all placed orders
        """
        # Extract and validate required parameters
        symbol = arguments.get("symbol")
        side = arguments.get("side")
        quantity = arguments.get("quantity")
        entry_type = arguments.get("entry_type")
        entry_price = arguments.get("entry_price")
        stop_price = arguments.get("stop_price")  # For STOP/STOP_MARKET/TAKE_PROFIT/TAKE_PROFIT_MARKET orders
        callback_rate = arguments.get("callback_rate")  # For TRAILING_STOP_MARKET orders
        activation_price = arguments.get("activation_price")  # Optional for TRAILING_STOP_MARKET
        take_profit_price = arguments.get("take_profit_price")
        stop_loss_price = arguments.get("stop_loss_price")
        position_side = arguments.get("position_side", "BOTH")
        time_in_force = arguments.get("time_in_force", "GTC")
        leverage = arguments.get("leverage")
        tp_type = arguments.get("tp_type", "LIMIT")  # Default to LIMIT for take-profit
        sl_type = arguments.get("sl_type", "LIMIT")  # Default to LIMIT for stop-loss
        
        # Validate required parameters
        if not all([symbol, side, quantity, entry_type, take_profit_price, stop_loss_price]):
            raise ValueError("Missing required parameters for bracket order")
        
        if side not in ["BUY", "SELL"]:
            raise ValueError("Side must be either 'BUY' or 'SELL'")
            
        valid_entry_types = ["LIMIT", "MARKET", "STOP", "STOP_MARKET", "TAKE_PROFIT", 
                          "TAKE_PROFIT_MARKET", "TRAILING_STOP_MARKET"]
        if entry_type not in valid_entry_types:
            raise ValueError(f"Entry type must be one of: {', '.join(valid_entry_types)}")
            
        # Validate parameters based on entry order type
        if entry_type in ["LIMIT", "STOP", "TAKE_PROFIT"] and not entry_price:
            raise ValueError(f"Entry price is required for {entry_type} orders")
            
        if entry_type in ["STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"] and not stop_price:
            raise ValueError(f"Stop price is required for {entry_type} orders")
            
        if entry_type == "TRAILING_STOP_MARKET" and not callback_rate:
            raise ValueError("Callback rate is required for TRAILING_STOP_MARKET orders")
            
        # Validate TP/SL types
        if tp_type not in ["LIMIT", "MARKET"]:
            raise ValueError("Take-profit type must be either 'LIMIT' or 'MARKET'")
            
        if sl_type not in ["LIMIT", "MARKET"]:
            raise ValueError("Stop-loss type must be either 'LIMIT' or 'MARKET'")
        
        # Set leverage if provided
        if leverage:
            try:
                await client._make_request(
                    "POST", 
                    "/fapi/v1/leverage", 
                    {"symbol": symbol, "leverage": leverage},
                    "USER_DATA"
                )
            except Exception as e:
                print(f"Warning: Failed to set leverage: {e}")
        
        # Determine opposite side for TP and SL orders
        opposite_side = "SELL" if side == "BUY" else "BUY"
        
        # Prepare result dictionary
        result = {
            "bracket_order": {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "position_side": position_side,
                "orders": {}
            }
        }
        
        try:
            # 1. Place entry order
            entry_params = {
                "symbol": symbol,
                "side": side,
                "positionSide": position_side,
                "quantity": quantity,
                "type": entry_type
            }
            
            # Set parameters based on entry order type
            if entry_type in ["LIMIT", "STOP", "TAKE_PROFIT"]:
                entry_params["price"] = entry_price
                entry_params["timeInForce"] = time_in_force
                
            if entry_type in ["STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"]:
                entry_params["stopPrice"] = stop_price
                
            if entry_type == "TRAILING_STOP_MARKET":
                entry_params["callbackRate"] = callback_rate
                if activation_price:
                    entry_params["activationPrice"] = activation_price
            
            entry_order = await client._make_request(
                "POST", 
                "/fapi/v1/order", 
                entry_params,
                "TRADE"
            )
            
            result["bracket_order"]["orders"]["entry"] = entry_order
            
            # For MARKET orders, we can place TP and SL immediately
            # For LIMIT orders, we would ideally use OCO orders or listen to order updates
            # but for simplicity, we'll place TP and SL orders immediately
            
            # 2. Place take-profit order
            tp_order_type = "TAKE_PROFIT" if tp_type == "LIMIT" else "TAKE_PROFIT_MARKET"
            tp_params = {
                "symbol": symbol,
                "side": opposite_side,
                "positionSide": position_side,
                "quantity": quantity,
                "type": tp_order_type,
                "stopPrice": take_profit_price,
                "reduceOnly": "true"  # Ensure it only reduces the position
            }
            
            # Add price and timeInForce only for LIMIT take-profit orders
            if tp_type == "LIMIT":
                tp_params["price"] = take_profit_price
                tp_params["timeInForce"] = time_in_force
            
            tp_order = await client._make_request(
                "POST", 
                "/fapi/v1/order", 
                tp_params,
                "TRADE"
            )
            
            result["bracket_order"]["orders"]["take_profit"] = tp_order
            
            # 3. Place stop-loss order
            sl_order_type = "STOP" if sl_type == "LIMIT" else "STOP_MARKET"
            sl_params = {
                "symbol": symbol,
                "side": opposite_side,
                "positionSide": position_side,
                "quantity": quantity,
                "type": sl_order_type,
                "stopPrice": stop_loss_price,
                "reduceOnly": "true"  # Ensure it only reduces the position
            }
            
            # Add price and timeInForce only for LIMIT stop-loss orders
            if sl_type == "LIMIT":
                sl_params["price"] = stop_loss_price
                sl_params["timeInForce"] = time_in_force
            
            sl_order = await client._make_request(
                "POST", 
                "/fapi/v1/order", 
                sl_params,
                "TRADE"
            )
            
            result["bracket_order"]["orders"]["stop_loss"] = sl_order
            
            return result
            
        except Exception as e:
            # If any order fails, attempt to cancel any successful orders
            if "orders" in result["bracket_order"]:
                for order_type, order in result["bracket_order"]["orders"].items():
                    if "orderId" in order:
                        try:
                            await client._make_request(
                                "DELETE", 
                                "/fapi/v1/order", 
                                {"symbol": symbol, "orderId": order["orderId"]},
                                "TRADE"
                            )
                        except Exception as cancel_error:
                            print(f"Failed to cancel {order_type} order: {cancel_error}")
            
            # Re-raise the original exception
            raise ValueError(f"Failed to place bracket order: {str(e)}")

    
    def _handle_top_gainers_losers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_top_gainers_losers tool"""
        request_type = arguments.get("type", "both").lower()
        limit = min(arguments.get("limit", 10), 200)  # Max 200
        min_volume = arguments.get("min_volume", 0)
        
        result = {}
        
        if request_type in ["gainers", "both"]:
            gainers = self.ticker_cache.get_top_gainers(limit)
            if min_volume > 0:
                gainers = [g for g in gainers if float(g.get('volume', 0)) >= min_volume]
            
            # Create a more compact representation of gainers
            compact_gainers = []
            for g in gainers[:limit]:
                compact_gainers.append({
                    "symbol": g.get("symbol", ""),
                    "pct": float(g.get("priceChangePercent", 0)),
                    "price": g.get("lastPrice", ""),
                    "volume": g.get("volume", ""),
                    "priceChange": g.get("priceChange", "")
                })
            result["gainers"] = compact_gainers
        
        if request_type in ["losers", "both"]:
            losers = self.ticker_cache.get_top_losers(limit)
            if min_volume > 0:
                losers = [l for l in losers if float(l.get('volume', 0)) >= min_volume]
            
            # Create a more compact representation of losers
            compact_losers = []
            for l in losers[:limit]:
                compact_losers.append({
                    "symbol": l.get("symbol", ""),
                    "pct": float(l.get("priceChangePercent", 0)),
                    "price": l.get("lastPrice", ""),
                    "volume": l.get("volume", ""),
                    "priceChange": l.get("priceChange", "")
                })
            result["losers"] = compact_losers
        
        # Add metadata
        result["metadata"] = {
            "last_updated": self.ticker_cache.last_updated.isoformat() if self.ticker_cache.last_updated else None,
            "total_symbols": len(self.ticker_cache.data),
            "filter_applied": {"min_volume": min_volume} if min_volume > 0 else None
        }
        
        return result
    
    def _handle_market_overview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_market_overview tool"""
        include_top_movers = arguments.get("include_top_movers", True)
        volume_threshold = arguments.get("volume_threshold", 0)
        
        # Filter data by volume threshold
        filtered_data = self.ticker_cache.data
        if volume_threshold > 0:
            filtered_data = [d for d in self.ticker_cache.data if float(d.get('volume', 0)) >= volume_threshold]
        
        # Calculate market statistics
        total_symbols = len(filtered_data)
        gainers_count = len([d for d in filtered_data if float(d.get('priceChangePercent', 0)) > 0])
        losers_count = len([d for d in filtered_data if float(d.get('priceChangePercent', 0)) < 0])
        unchanged_count = total_symbols - gainers_count - losers_count
        
        # Calculate total market volume
        total_volume = sum(float(d.get('volume', 0)) for d in filtered_data)
        
        result = {
            "market_summary": {
                "total_symbols": total_symbols,
                "gainers": gainers_count,
                "losers": losers_count,
                "unchanged": unchanged_count,
                "total_24h_volume": total_volume,
                "last_updated": self.ticker_cache.last_updated.isoformat() if self.ticker_cache.last_updated else None
            }
        }
        
        if include_top_movers:
            top_gainers = self.ticker_cache.get_top_gainers(5)
            top_losers = self.ticker_cache.get_top_losers(5)
            
            if volume_threshold > 0:
                top_gainers = [g for g in top_gainers if float(g.get('volume', 0)) >= volume_threshold][:5]
                top_losers = [l for l in top_losers if float(l.get('volume', 0)) >= volume_threshold][:5]
            
            result["top_movers"] = {
                "top_gainers": top_gainers,
                "top_losers": top_losers
            }
        
        return result
