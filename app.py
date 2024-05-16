import streamlit as st
import numpy as np
import xlsxwriter
import graphviz
import base64
import io

from streamlit_extras.badges import badge
from funcs import *

def main():
    col1, col2, col3 = st.columns([0.0425, 0.265, 0.035])
    
    with col1:
        st.image("https://github.com/tsu2000/binom_tree/raw/main/images/weigh_prices.png")

    with col2:
        st.title(" BOPM Visualisation")

    with col3:
        badge(type = "github", name = "tsu2000/binom_tree", url = "https://github.com/tsu2000/binom_tree")

    st.markdown("#### Visualising the Binomial Options Pricing Model (BOPM)")
    st.markdown("For valuation and quantitative finance students to better understand the Binomial Options Pricing Model (BOPM) for pricing European and American call and put options. Values have been rounded off to 4 d.p.")

    # Get user inputs
    col_a, col_b = st.columns([0.5 ,0.5])
    with col_a:
        S0 = st.number_input("Initial stock price: $(S_0)$", min_value = 0.00, max_value = 100000000.00, value = 15.00, step = 0.01)
        T = st.number_input("Time to maturity **(in years)**: $(T)$", min_value = 0.000001, max_value = 1000.000000, value = 1.000000, step = 0.000001, format = "%0.6f")
        r = st.number_input("Annual discount rate (Continuous compounding): $(r)$", min_value = 0.0000, max_value = 10000.0000, value = 0.0800, step = 0.0001, format = "%0.4f")
        opt_type = st.radio("Option type (Either call or put):", ['Call', 'Put'], horizontal = True, captions = ['Right to buy an asset', 'Right to sell an asset'])

    with col_b:
        K = st.number_input("Strike price: $(K)$", min_value = 0.00, max_value = 100000000.00, value = 14.00, step = 0.01)
        N = st.number_input("Number of future periods: $(N)$", min_value = 1, max_value = 50, value = 2, step = 1) 
        v = st.number_input("Annual stock volatility $(\sigma)$", min_value = 0.0000, max_value = 10000.0000, value = 0.2500, step = 0.0001, format = "%0.4f") 
        deriv_type = st.radio("Style of option:", ['European', 'American'], horizontal = True, captions = ['Exercise at expiration', 'Exercise-flexible']) 

    u, d, p, pp_dict = binomial_tree(S0, K, T, N, r, v, opt_type, deriv_type)

    result = final_pairs_str(pp_dict = pp_dict, all_pairs = generate_step_pairs(N))

    st.write('---')

    st.markdown("**Parameters given:**")

    st.latex(f"S_0 = {S0}, \quad K = {K}, \quad T = {np.round(T, 4)}, \quad N = {N},  \quad \Delta t = {np.round(T/N, 4)}, \quad r = {r}, \quad \sigma = {v}")

    display_str = f"""digraph {{
        rankdir="LR"
        node [shape="box" width="1.6" fontname="Arial"]
        {result};
        }}       
        """

    st.graphviz_chart(display_str, use_container_width = True)

    st.latex(f"u = {np.round(u, 4)}, \quad d = {np.round(d, 4)}, \quad p = {np.round(p, 4)}, \quad 1 - p = {np.round(1 - p, 4)}")

    col_x, col_y = st.columns([1, 0.36])

    with col_x:
        # Obtain data from calculations and write to .xlsx file
        def to_excel():
            output = io.BytesIO()
            
            # Create a new Excel workbook
            workbook = xlsxwriter.Workbook(output)

            # Add a worksheet to the workbook
            worksheet = workbook.add_worksheet("tree_vals")

            # Add formats and templates here
            current_payoff = workbook.add_format(
                {
                    'bg_color': '#DAF2D0',
                    'bold': True,
                    'border': 1,
                    'num_format': '0.0000' 
                }
            )

            header_format = workbook.add_format(
                {
                    'bold': True,
                    'underline': True,
                    'align': 'left'
                }
            ) 

            variable_format = workbook.add_format(
                {
                    'bold': True,
                    'align': 'right'
                }
            )
            
            user_str_format = workbook.add_format(
                {
                    'align': 'right'
                }
            )  

            numeric_format = workbook.add_format(
                {
                    'num_format': '0.0000'
                }
            ) 

            description_format = workbook.add_format(
                {
                    'italic': True
                }
            )

            # Write data to the worksheet
            worksheet.write("A1", "User inputs:", header_format)
            worksheet.write("A12", "Calculated constants:", header_format)
            worksheet.write("A18", "Prices and payoffs:", header_format)

            variables = ["S_0", "K", "T", "N", "Δt", "r", "σ", "Opt Type", "Opt Style"]
            constants = ["u", "d", "p", "1 - p"]

            r1, c1 = 1, 0
            for i in variables:
                worksheet.write(r1, c1, i, variable_format)
                r1 += 1

            r2, c2 = 12, 0
            for j in constants:
                worksheet.write(r2, c2, j, variable_format)
                r2 += 1

            worksheet.write("B2", S0, numeric_format)
            worksheet.write("B3", K, numeric_format)
            worksheet.write("B4", T, numeric_format)
            worksheet.write("B5", N, numeric_format)
            worksheet.write("B6", T/N, numeric_format)
            worksheet.write("B7", r, numeric_format)
            worksheet.write("B8", v, numeric_format)
            worksheet.write("B9", opt_type, user_str_format)
            worksheet.write("B10", deriv_type, user_str_format)

            worksheet.write("B13", u, numeric_format)
            worksheet.write("B14", d, numeric_format)
            worksheet.write("B15", p, numeric_format)
            worksheet.write("B16", 1 - p, numeric_format) 

            r3, c3 = 18, 0
            sorted_dict = dict(sorted(pp_dict.items(), key=lambda x: x[0]))
            for key, val in sorted_dict.items():
                worksheet.write(r3, c3, f"Price {key}", variable_format)
                c3 += 1
                worksheet.write(r3, c3, val[0], numeric_format)
                c3 += 1
                worksheet.write(r3, c3, f"Payoff {key}", variable_format)
                c3 += 1
                worksheet.write(r3, c3, val[1], numeric_format)
                c3 -= 3
                r3 += 1

            worksheet.write("D19", pp_dict[1][1], current_payoff)

            worksheet.write("D2", "Initial stock price", description_format)
            worksheet.write("D3", "Strike price", description_format)
            worksheet.write("D4", "Time to maturity (in years)", description_format)
            worksheet.write("D5", "No. of future periods", description_format)
            worksheet.write("D6", "Time step between each period (T/N)", description_format)
            worksheet.write("D7", "Annual discount rate (continuous compounding)", description_format)
            worksheet.write("D8", "Annual stock volatility", description_format)
            worksheet.write("D9", "Type of option (Call or Put)", description_format)
            worksheet.write("D10", "Style of option (European or American)", description_format)

            worksheet.write("D13", "Up rate of the stock", description_format)
            worksheet.write("D14", "Down rate of the stock", description_format)
            worksheet.write("D15", "Probability stock price will go up (by u) in next period", description_format)
            worksheet.write("D16", "Probability stock price will go down (by d) in next period", description_format)

            # Set width of columns
            worksheet.set_column("A:A", 10)
            worksheet.set_column("B:B", 16)
            worksheet.set_column("C:C", 10)
            worksheet.set_column("D:D", 16)

            # Hide gridlines in the worksheet
            worksheet.hide_gridlines(2)

            # Saving and returning data
            workbook.close()
            processed_data = output.getvalue()

            return base64.b64encode(processed_data).decode()

        href = f'<a href="data:application/octet-stream;base64,{to_excel()}" download="btree_details.xlsx">📝 Download data (.xlsx)</a>' 
        st.markdown(href, unsafe_allow_html = True)

    with col_y:
        # Turn graph into graphviz object
        graph = graphviz.Source(display_str)

        # Render the graph as a PDF file
        def to_pdf(graph):
            pdf_data = graph.pipe(format = 'pdf')
            pdf_base64 = base64.b64encode(pdf_data).decode()
            return pdf_base64

        # Provide a download button for the PDF image
        href = f'<a href="data:application/pdf;base64,{to_pdf(graph)}" download="btree_graph.pdf">📈 Download graph (.pdf)</a>'
        st.markdown(href, unsafe_allow_html = True)

    st.markdown(f"##### Current Payoff at time $T_0$ = {np.round(pp_dict[1][1], 4)}")

    with st.expander("How does the Binomial Options Pricing Model work?"):
        st.markdown("The Binomial Options Pricing Model estimates option prices by simulating the possible movements of an asset's price over time, assuming it can only move up or down by a specified fixed amount and that the risk-neutral probabilities of these movements are known.")
        
        st.markdown("#### Call and Put Options")
        st.markdown("""
            A call option gives the holder the right, but not the obligation, to buy an underlying asset at a predetermined price (the strike price) before or at the expiration date. Investors purchase call options when they anticipate that the price of the underlying asset will rise above the strike price before the option expires. This allows them to buy the asset at a lower price and potentially sell it at the current market price, thus profiting from the difference.\\
            
            For example, if you purchase a call option with a strike price of $50 for a stock currently trading at $45, and the stock price rises to $60, you can buy the stock at $50 and either sell it at $60 or hold it for further gains.\\
            
            A put option gives the holder the right, but not the obligation, to sell an underlying asset at the strike price before or at the expiration date. Investors purchase put options when they expect the price of the underlying asset to fall below the strike price. This allows them to sell the asset at a higher price than the market price, thus profiting from the difference.\\
            
            For instance, if you purchase a put option with a strike price of $50 for a stock currently trading at $55, and the stock price drops to $40, you can sell the stock at $50 and potentially repurchase it at $40, thus making a profit.\\
            
            In summary:
            - Purchase a call option if you expect the underlying asset's price to **rise**.
            - Purchase a put option if you expect the underlying asset's price to **fall**.
        """)

        st.markdown("#### European and American Options")
        st.markdown("American options can be exercised at any point up to and including the expiration date, providing greater flexibility to the holder. European options, on the other hand, can only be exercised on the expiration date itself, limiting the holder's ability to react to market changes before that date.")
        
        st.markdown("#### Binomial Tree (One-period)")
        st.image("https://raw.githubusercontent.com/tsu2000/binom_tree/main/images/binom_tree_1_period.png")
        st.markdown("These are some of the key variables that go into the creation of the binomial tree in the BOPM. Note that future stock prices are uncertain and will change at each time length of step in the binomial tree structure. A multi-period binomial tree consists of multiple one-period binomial trees.")
        
        st.markdown("#### Steps used to value the option")
        
        st.markdown("**Step 1:** Using stock volatility ($\sigma$) to estimate $u$ and $d$")
        st.latex(r"""
            u \times d = e^{\sigma \sqrt{\Delta t}} \times e^{-\sigma \sqrt{\Delta t}} = e^0 = 1
            \\
            u = e^{\sigma \sqrt{\Delta t}}
            \\
            d = e^{-\sigma \sqrt{\Delta t}}         
        """)
        st.markdown("""
            $u$: Up rate in price\\
            $d$: Down rate in price\\
            $\sigma$: Volatility (Measures the standard deviation of stock returns)\\
            $\Delta t$: Time length of each step in binomial lattice, with units in years (Assume 365 days a year for binomial pricing)
        """)
        st.markdown(r"For example, if each step is $n$ days long, $\Delta t$ = $\frac{n}{365}$.")

        st.markdown("**Step 2:** Using $r, \Delta t, u, d$ to estimate $p$")
        st.latex(r"""
            e^{-r \Delta t} \left( u \times p + d \times (1 - p) \right) S_0 = S_0
            \\
            p = \frac{e^{r \Delta t} - d}{u - d}       
        """)
        st.markdown("""
            $S_0$: Price at the current period\\
            $r$: Discount rate\\
            $\Delta t$: The time length of each step in the binomial lattice (unit: years)\\
            $p$: Probability that price will go up by factor of $u$ at the next period\\
            $1 - p$: Probability that price will go down by factor of $d$ at the next period\\
            $u$: Up **rate** in price\\
            $d$: Down **rate** in price
        """)
        st.markdown("**Step 3:** Plot nodes of binomial tree for future stock price movements")
        st.markdown("For example, for a binomial tree with maturing option in 2 future periods:")
        st.latex(r"""
            \begin{align*}
            & \text{Period 0: } S_0 \\
            & \text{Period 1: } S_0 \times u, S_0 \times d\\
            & \text{Period 2: } S_0 \times u \times u, S_0 \times u \times d, S_0 \times d \times d              
            \end{align*}           
        """)
        st.markdown("""
            $S_0$: Price at the current period\\
            $u$: Up **rate** in price\\
            $d$: Down **rate** in price
        """)
        st.markdown("Visually, it may be represented like this:")
        a, b, c = st.columns([0.3, 0.4, 0.3])
        with a:
            st.write('')
        
        with b:
            st.graphviz_chart('''
                digraph {
                    rankdir="LR"
                    node [shape="circle", width=0.5, height=0.5, fixedsize = "true"]
                    S0[label=<S<SUB>0</SUB>>]
                    Su[label=<S<SUB>u</SUB>>]
                    Sd[label=<S<SUB>d</SUB>>]
                    Suu[label=<S<SUB>uu</SUB>>]
                    Sud[label=<S<SUB>ud</SUB>>]
                    Sdd[label=<S<SUB>dd</SUB>>]
                    S0 -> Su
                    S0 -> Sd
                    Su -> Sud
                    Su -> Suu
                    Sd -> Sud
                    Sd -> Sdd
                }
            ''', use_container_width = True)
        with c:
            st.write('')
        st.markdown("If there are too many periods, consider using software to calculate the payoffs instead.")

        st.markdown("**Step 4:** Estimate return (payoff) of exercising option at maturity")
        st.markdown("At option maturity, decide whether you want to exercise under each node by computing the respective intrinsic value. For each node at maturity, compute:")
        st.latex(r"""
            \text{Payoff}_S = \max(S - K, 0) \text{ - If option in question is a call}
            \\
            \text{Payoff}_S = \max(K - S, 0) \text{ - If option in question is a put}    
        """)
        st.markdown("""
            $K$: Strike price\\
            $S$: Computed future stock price
        """)

        st.markdown("**Step 5:** Estimate the present value of the returns")
        st.markdown("Because of the time value of money, we must discount future returns back through the binomial lattice in order to obtain the present value (PV) of the returns (payoffs). For example, for a binomial tree with a maturing option in 2 future periods:")
        st.markdown("*Get estimated PV from period 2 to period 1*")
        st.latex(r"""
            \text{PV}_{S_u} = [\text{Payoff}_{S_{uu}} \times p + \text{Payoff}_{S_{ud}} \times (1 - p)] \times e^{-r \Delta t}
            \\
            \text{PV}_{S_d} = [\text{Payoff}_{S_{dd}} \times p + \text{Payoff}_{S_{ud}} \times (1 - p)] \times e^{-r \Delta t} 
        """)
        st.markdown("""
            $\\text{Payoff}_S$: The payoff **(not price)** at the node S\\
            $\\text{PV}_S$: The present value of the payoff **at the node S** discounted from the future possible periods for the node.\\
            $p$: Probability that price will go up by factor of $u$ at the next period\\
            $r$: Discount rate\\
            $\Delta t$: The time length of each step in the binomial lattice (unit: years)\\
            $e^{-r \Delta t}$: The discount factor which calculates the present value of future cash flows (continuous compounding)
        """)
        st.markdown("*Get estimated PV from period 1 to period 0*")
        st.markdown("If option is European:")
        st.markdown(r"""
            - For a European option, we simply discount the $\text{PV}$s back through the time steps of the binomial lattice.
            - There is no need to compare bewteen the discounted payoff value and payoff value at the node since there is no early exercise option.
        """)
        st.latex(r"""
            \text{Payoff}_{S_0} = [\text{PV}_{S_u} \times p + \text{PV}_{S_d}  \times (1 - p)] \times e^{-r \Delta t}
        """) 
        st.markdown("If option is American:")
        st.markdown(r"""
            - There is a need to compare the discounted payoff value at each node from the penultimate time step onward due to early exercise option. The resulting payoff would be the higher of the current payoff at S, or the discounted payoff at S (this means you get more returns from waiting longer)
            - Repeat step 4 at the intermediate nodes in period 1, but replace 0 in the $\max$ function with the appropriate discounted payoff value from period 2.
            - So for example, at $S_u$ for a call option, $\text{Payoff}_{S_u} = \max(S_u - K, \text{PV}_{S_u})$.
            - Likewise, at $S_d$ for a call option, $\text{Payoff}_{S_d} = \max(S_d - K, \text{PV}_{S_d})$.
            - Take the higher of the 2 as final period 1 payoff, then get estimated PV from period 1 to period 0 as per European option.
        """)
        st.markdown("Therefore, for an American call option:")
        st.latex(r"""
            \text{Payoff}_{S_0} = [ \max(S_u - K, \text{PV}_{S_u}) \times p + \max(S_d - K, \text{PV}_{S_d}) \times (1 - p)] \times e^{-r \Delta t}
        """)
        st.markdown("For models with more than 2 future time periods, step 5 may have to be repeated multiple times to discount the PV back by multiple periods.")

        st.markdown("The final payoff at $S_0$ would be equal to the present value of all future options returns. If you are still unsure of the process, you can try downloading the Excel file and PDF of the binomial tree and try manually to get the same payoff results as the program.")




if __name__ == "__main__":
    st.set_page_config(page_title = "BOPM Visusalisation", page_icon = "💵")
    main()
