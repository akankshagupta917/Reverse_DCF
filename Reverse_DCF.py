import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd 
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.graph_objects as go


external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/lux/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, meta_tags=[{'name': 'author', 'content': 'Akanksha Gupta'}])
app.title = "Reverse DCF"
server = app.server

layout1 = html.Div([
	html.Div("This site provides interactive tools to valuate and analyze stocks through Reverse DCF model. Check the navigation bar for more.")
	])

layout2 = html.Div([
    html.H1("Valuing Consistent Compounders", style={'box-sizing': 'border-box', 'color': 'rgb(26, 26, 26)'}),
    html.P("Hi there!"),
    html.P("This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model."),
    html.P("We then compare this with current PE of the stock to calculate degree of overvaluation."),
    html.Div([
        html.Label("NSE/BSE symbol", htmlFor="nse-bse-input", style={'display':'block'}),
        dcc.Input(id="nse-bse-input", type="text", placeholder="Enter symbol here", value ='NESTLEIND'),
       ]),
    html.Div([
		html.Div([
    		html.Label("Cost of Capital	(CoC): %", style={'display':'block'}),
    		dcc.Slider(8, 16, 0.5, value=12, marks={i: str(i) for i in range(8, 17)}, id='cost_of_capital')
    		]),
    	html.Div([
    		html.Label("Return on Capital Employed (RoCE): %", style={'display':'block'}),
    		dcc.Slider(10, 100, 5, value=20, marks={i: str(i) for i in range(10, 101, 10)}, id ="pre_tax_roc") ]),
    	html.Div([
    		html.Label("Growth during high growth period: $", style={'display':'block'}),
    		dcc.Slider(8, 20, 1, value=12,  marks={i: str(i) for i in range(8, 21) if i % 2 == 0}, id="earnings_growth_rate")
    		]),
    	html.Div([
    		html.Label("High growth period(years)"),
    		dcc.Slider(10, 25, 1, value=15,  marks={**{i: str(i) for i in range(10, 26) if i % 2 == 0}, 25: '25'}, id="earnings_growth_years")]),
    	html.Div([
    		html.Label("Fade period(years):", style={'display':'block'}),
    		dcc.Slider(5, 20, 5, value=15, disabled=True, id="fade_period")
    		]),
    	html.Div([
    		html.Label("Terminal growth rate: %", style={'display':'block'}),
    		dcc.Slider(0, 7.5, 0.5, value=5, marks={i: str(i) for i in range(0, 9) if i <= 7.5}, id="terminal_growth_rate")
    		], style={'margin-bottom':'2'})
    		]), 
   
    html.Div([
    	html.P(id='stock_symbol', style={'line-height':'0'}),
    	html.P(id='current_pe', style={'line-height':'0.5'}),
    	html.P(id='fy23pe', style={'line-height':'0.5'}),
    	html.P(id = 'roce', style={'line-height':'0.5'})
    	]),
    	
    dash_table.DataTable(
        id='table'),
   
    dbc.Row([
    dbc.Col([
    	dcc.Graph(figure={}, id = 'graph-display'),], width=6),
    dbc.Col([
    	dcc.Graph(figure= {}, id = 'graph-display2'),],width=6)]),
    html.Div([
    	html.P("Play with inputs to see changes in intrinsic PE and overvaluation:", style={'margin-bottom':'0'}),
		html.P(id="intrinsic_pe", style={'margin-bottom':'0', 'margin-top':'0'}),
		html.P(id="overvaluation", style={'margin-top':'0'})
    	])
    	
    	])




app.layout = html.Div([
	html.Div([

		dbc.NavbarSimple(
			children=[
        
        dbc.DropdownMenu( 
            children=[
                dbc.DropdownMenuItem("Home", href= '/'),
                dbc.DropdownMenuItem("DCF Valuation", href="/dcf"),
            ],
            nav=True,
            in_navbar=True,
            label="Pages",
			className ="ms-auto"),],
    brand="Reverse DCF",
    brand_href="/home",
    color="primary",
    dark=True,
    style={'margin-bottom':'24px'},
    className = 'bg-dark'),
    ]),
    dcc.Location(id='url', refresh=False), 
    html.Div(id='page-content'), 
    
    ])
    


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dcf':
        return layout2
    else: 
        return layout1



@app.callback(
    [Output('graph-display', 'figure'), 
     Output('graph-display2', 'figure'),
     Output('stock_symbol', 'children'),
     Output('current_pe', 'children'),
     Output('fy23pe', 'children'),
     Output('roce', 'children'),
     Output('table', 'data')],
    [Input('nse-bse-input', 'value')]
)
def display_graph(value):
	base_url = f"https://www.screener.in/company/{value}/"  
	c_url = base_url + 'consolidated/'


	page = requests.get(c_url)
	soup = BeautifulSoup(page.content, 'html.parser')
	
	company_links = soup.find('div', class_='company-links show-from-tablet-landscape')
	company_symbol = company_links.find_all('span', class_='ink-700 upper')[1]
	text1 = "Stock Symbol: " + company_symbol.get_text().split(':')[1].strip()
	
	
	company_ratios = soup.find('div', class_='company-ratios')
	span_element = soup.find_all('span', class_='number')[4]
	if span_element.text.strip() == '':
		page = requests.get(base_url)
		soup = BeautifulSoup(page.content, 'html.parser')
		company_ratios = soup.find('div', class_='company-ratios')		
		span_element = soup.find_all('span', class_='number')[4]
		text2 = "Current PE: " + span_element.get_text()
	else:
		text2 = "Current PE: " + span_element.get_text()
	
	
	market_cap = company_ratios.find_all('span', class_='number')[0]
	market_cap = market_cap.get_text()
	market_cap= market_cap.replace(',', '')
	market_cap_int = int(market_cap)
	
	html_content = str(soup)
	dfs = pd.read_html(html_content)
	second_table = dfs[1]
	value1 = second_table.iloc[-3, -2]
	desired_value = int(value1)
	
	
	market_cap_computed = round((market_cap_int/desired_value), 1)
	market_cap_text = 'FY23PE: ' + str(market_cap_computed)

	seventh_table = dfs[8]
	roce = seventh_table.iloc[-1, 8]
	roce_text = "5-yr median pre-tax RoCE: " + str(roce) 

	df1 = dfs[2]
	df2 = dfs[3]
	
	headings = df1.iloc[:, 0]
	values_df1 = df1.iloc[:, 1]
	values_df2 = df2.iloc[:, 1]
	
	merged_df = pd.DataFrame({
	'Sales Growth': values_df1.values,
	'Profit Growth': values_df2.values
	}, index=headings)
	transposed_df = merged_df.T
	transposed_df.index.name = ''
	data = transposed_df.reset_index().to_dict('records')
	
	df1["Compounded Sales Growth.1"] = df1["Compounded Sales Growth.1"].str.rstrip('%').astype('float')
	df2["Compounded Profit Growth.1"] = df2["Compounded Profit Growth.1"].str.rstrip('%').astype('float')
	fig1 = px.bar(df1, y='Compounded Sales Growth', x='Compounded Sales Growth.1', 
             orientation='h', 
             labels={'Compounded Sales Growth.1': 'Sales Growth (%)', 'Compounded Sales Growth': 'Time Period'})
	fig2 = px.bar(df2, y='Compounded Profit Growth', x='Compounded Profit Growth.1', 
             orientation='h', 
             labels={'Compounded Profit Growth.1': 'Profit Growth (%)', 'Compounded Profit Growth': 'Time Period'})
	
	return fig1, fig2, text1, text2, market_cap_text, roce_text, data





@app.callback(
Output('intrinsic_pe', 'children'),
[Input('cost_of_capital', 'value'),
 Input ('pre_tax_roc', 'value'),
 Input ('earnings_growth_rate', 'value'),
 Input ('earnings_growth_years', 'value'),
 Input ('fade_period', 'value'),
 Input ('terminal_growth_rate', 'value')])

def get_intrinsic_value(cost_of_capital, pre_tax_roc, earnings_growth_rate, earnings_growth_years, fade_period, terminal_growth_rate):
	cost_of_capital = int(cost_of_capital)/100
	tax_rate = 0.25
	post_tax_roc = (pre_tax_roc*(1-tax_rate)/100)
	earnings_growth_rate = [earnings_growth_rate/100]
	terminal_growth_rate = terminal_growth_rate/100
	reinvestment_rate1 = earnings_growth_rate[0]/post_tax_roc
	reinvestment_rate2 = terminal_growth_rate/post_tax_roc
	nopat = [(post_tax_roc*100)] 
	ebt = nopat[0]/(1-tax_rate)
	investment = nopat[0]*reinvestment_rate1
	capital_ending = 100 + investment
	fcf = nopat[0] - investment 
	discount_factor = 1
	discount_fcf = 0 
	sum_discount_fcf = 0 
	year = fade_period + earnings_growth_years + 1
	total = 3

	for i in range (0, earnings_growth_years):
		new_value = capital_ending*post_tax_roc
		nopat.append(new_value)
	
		ebt = nopat[i+1]/(1-tax_rate)
		new_value2 = nopat[i+1]/nopat[i]-1
		earnings_growth_rate.append(new_value2)
		investment = nopat[i+1]*reinvestment_rate1
		fcf = nopat[i+1] - investment
		capital_ending += investment
		discount_factor = 1/(1+cost_of_capital)**(i+1)	
		discount_fcf = round((fcf*discount_factor), 2)

		total += discount_fcf

	new_value2 = earnings_growth_rate[9] - (earnings_growth_rate[0] - terminal_growth_rate)/fade_period
	earnings_growth_rate.append(new_value2)

	for i in range (earnings_growth_years, (15+fade_period)):
		new_value = capital_ending*post_tax_roc
		nopat.append(new_value)
		ebt = nopat[-1]/(1-tax_rate)
		investment = earnings_growth_rate[-1]/post_tax_roc * nopat[-1]
		capital_ending += investment
		fcf = nopat[-1] - investment
		discount_factor = (1/(1+cost_of_capital)) **(i+1)
		discount_fcf = fcf*discount_factor
		total += discount_fcf
		new_value2 = earnings_growth_rate[-1] - (earnings_growth_rate[0] - terminal_growth_rate)/fade_period
		earnings_growth_rate.append(new_value2)
	
	nopat_tv = nopat[-1]*(1+terminal_growth_rate)/(cost_of_capital - terminal_growth_rate)
	investment_tv = nopat_tv * reinvestment_rate2
	fcf_tv = nopat_tv - investment_tv
	discounted_fcf_tv = fcf_tv* discount_factor
	intrinsic_value = discounted_fcf_tv + total
	ttm_pe = round(intrinsic_value/ nopat[0], 2)
	
	return "The calculated intrinsic PE is: " + str(ttm_pe)




@app.callback(
Output('overvaluation', 'children'),
[Input('current_pe', 'children'),
 Input ('fy23pe', 'children'),
 Input('intrinsic_pe', 'children')])

def get_overvaluation(current_pe, fy23pe, intrinsic_pe):
	current_pe = float(str(current_pe.split(':')[1].strip()))
	fy23pe = float(str(fy23pe.split(':')[1].strip()))
	intrinsic_pe = float(str(intrinsic_pe.split(':')[1].strip()))
	
	if current_pe > fy23pe :
		return "Degree of overvaluation: " + str(int(((fy23pe/intrinsic_pe) - 1)*100)) + "%"
	else:
		return "Degree of overvaluation: " + str(int(((current_pe/intrinsic_pe) - 1)*100)) + "%"
		
 	





if __name__ == '__main__':
    app.run_server(debug=True)
