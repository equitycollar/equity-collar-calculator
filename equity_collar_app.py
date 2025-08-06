# Equity Collar Calculator (Streamlit Version for WordPress Embed)

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

st.set_page_config(page_title="Equity Collar Calculator", layout="centered")
st.title("Equity Collar Calculator")

# User Inputs
ticker = st.text_input("Stock Ticker", "AAPL")
entry_price = st.number_input("Entry Price", min_value=0.0, value=160.0, step=0.5)
shares = st.number_input("Number of Shares", min_value=1, value=100, step=10)
put_strike = st.number_input("Put Strike", min_value=0.0, value=150.0, step=1.0)
call_strike = st.number_input("Call Strike", min_value=0.0, value=175.0, step=1.0)
expiration = st.text_input("Option Expiration (YYYY-MM-DD)", "2025-12-20")

if st.button("Calculate Collar"):
    try:
        stock = yf.Ticker(ticker)
        options = stock.option_chain(expiration)
        puts = options.puts
        calls = options.calls

        put_row = puts[puts['strike'] == put_strike].iloc[0]
        call_row = calls[calls['strike'] == call_strike].iloc[0]

        put_premium = put_row['ask']
        call_premium = call_row['bid']
        net_premium = call_premium - put_premium

        max_loss = (put_strike - entry_price + net_premium) * shares
        max_gain = (call_strike - entry_price + net_premium) * shares

        breakeven_low = entry_price + net_premium if net_premium < 0 else put_strike
        breakeven_high = entry_price + net_premium if net_premium > 0 else call_strike

        # Display Summary
        st.subheader("Results")
        st.write(f"**Net Premium (Credit/Debit):** ${net_premium:.2f}")
        st.write(f"**Max Gain:** ${max_gain:,.2f}")
        st.write(f"**Max Loss:** ${max_loss:,.2f}")
        st.write(f"**Breakeven Range:** ${breakeven_low:.2f} to ${breakeven_high:.2f}")

        # Payoff Chart
        import matplotlib.pyplot as plt
        prices = np.linspace(put_strike - 20, call_strike + 20, 100)
        payoffs = []
        for price in prices:
            intrinsic_put = max(put_strike - price, 0)
            intrinsic_call = max(price - call_strike, 0)
            value = (price - entry_price - intrinsic_put + intrinsic_call + net_premium) * shares
            payoffs.append(value)

        fig, ax = plt.subplots()
        ax.plot(prices, payoffs, label="Payoff")
        ax.axhline(0, color='gray', linestyle='--')
        ax.axvline(put_strike, color='red', linestyle='--', label='Put Strike')
        ax.axvline(call_strike, color='green', linestyle='--', label='Call Strike')
        ax.set_title("Equity Collar Payoff at Expiration")
        ax.set_xlabel("Stock Price at Expiration")
        ax.set_ylabel("Net Profit / Loss ($)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
