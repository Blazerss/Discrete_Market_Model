import numpy as np


def PriceDynamicsBi(periods,number_assets, initial_values,rate, factors):
    """
    :param periods: number of periods for the process
    :param number_assets: how many assets' process you want to create
    :param initial_values: initial values for the asset or assets
    :param factors: up and down factor
    :param rate: periodic interest rate
    :return: asset process or assets processes and martingale measure
    """

    if number_assets == 1:
        stock_values = np.empty((periods, periods))
        stock_values[:] = np.nan
        stock_values[0,0] = initial_values
        for i in range(1, periods):
            changes = []
            if i == 1:
                stock_values[ i, :i + 1] = stock_values[ i - 1, :i] * factors
            else:
                for j in range(len(stock_values[ i - 1, :i])):
                    if j != range(len(stock_values[ i - 1, :i]))[-1]:
                        changes.append(stock_values[ i - 1, j] * factors[ 0])

                    else:
                        changes.append(stock_values[ i - 1, j] * factors[ 0])
                        changes.append(stock_values[ i - 1, j] * factors[ 1])

                stock_values[ i, :i + 1] = changes
        Q = ((1 + rate) - factors[1]) / (factors[0] - factors[1])
        Q = np.array(((Q,1-Q)))
        return stock_values,Q


    if number_assets > 1:
        stock_values = np.empty((number_assets, periods, periods))
        stock_values[:] = np.nan
        for i in range(number_assets):
            stock_values[i, 0, 0] = initial_values[i]

        for g in range(0, number_assets):
            for i in range(1, periods):
                changes = []
                if i == 1:

                    stock_values[g, i, :i + 1] = stock_values[g, i - 1, :i] * factors[g,]
                else:
                    for j in range(len(stock_values[g, i - 1, :i])):
                        if j != range(len(stock_values[g, i - 1, :i]))[-1]:
                            changes.append(stock_values[g, i - 1, j] * factors[g, 0])

                        else:
                            changes.append(stock_values[g, i - 1, j] * factors[g, 0])
                            changes.append(stock_values[g, i - 1, j] * factors[g, 1])

                    stock_values[g, i, :i + 1] = changes
        A = np.array([[stock_values[0,1,0]/(1+rate), stock_values[0,1,1]/(1+rate)],
                      [stock_values[1,1,0]/(1+rate), stock_values[1,1,1]/(1+rate)]])
        y = np.array([initial_values[0], initial_values[1]])
        Q = np.linalg.solve(A, y)
        return stock_values,Q

def PriceDynamicsTri(periods,number_assets, initial_values,rate, factors):
    """
    :param periods: number of periods for the process
    :param number_assets: how many assets' process you want to create
    :param initial_values: initial values for the asset or assets
    :param factors: up and down factor
    :param rate: periodic interest rate
    :return: if asset is one then it returns only the process, if assets more than one it returns the process and the martingale measure
    """


    # we can use numpy to solve the system so we return only the process
    if number_assets ==1:
        S = np.empty(( periods + (periods - 1), periods))
        S[:] = np.nan
        S[periods-1,0]= initial_values

        for i in range(1, periods):
            S[ :, i] = S[ :, i - 1]
            S[ periods - 1 - i, i] = S[periods - i, i] * factors[ 0]
            S[ periods - 1 + i, i] = S[periods + i - 2, i] * factors[ 1]

        return S
    # we can use numpy to solve the system so we can return also the martingale measure
    if number_assets >1:
        S = np.empty((number_assets, periods + (periods - 1), periods))
        S[:] = np.nan
        for i in range(number_assets):
            S[i, periods - 1, 0] = initial_values[i]
        for g in range(0, number_assets):
            for i in range(1, periods):
                S[g, :, i] = S[g, :, i - 1]
                S[g, periods - 1 - i, i] = S[g, periods - i, i] * factors[g, 0]
                S[g, periods - 1 + i, i] = S[g, periods + i - 2, i] * factors[g, 1]

        A = np.array([[1,1,1],
                      [S[0, periods, 1]/(1+rate), S[0, periods-1, 1]/(1+rate),S[0,periods-2,1]/(1+rate)],
                      [S[1, periods, 1]/(1+rate), S[1, periods-1, 1]/(1+rate),S[1,periods-2,1]/(1+rate)]])
        y = np.array([1,initial_values[0], initial_values[1]])
        Q = np.linalg.solve(A, y)
        return S,Q




def OptionValue(stock, strike,maturity, Martingale,rate, call=True, american=False):
    """
    :param stock: process of the asset with 2 dimensions
    :param strike: scalar value for the strike of the contract
    :param maturity: how many periods ahead the end of the contract is, w.r.t. the initial period
    :param Martingale: Martingale measure to apply risk neautral valuation formula
    :param rate: periodic rate of return
    :param call: boolean value to switch from call to put option
    :param american: boolean value to switch from european to american option
    :return: process of the value of the option
    """

    if np.isnan(stock[-1,:]).sum() == 0:
        if call:
            payoff = 'np.maximum(stock[i,j] - strike,0)'
        else:
            payoff = 'np.maximum( strike - stock[i,j] ,0)'

        call_value = np.empty_like(stock)
        call_value[:] = np.nan

        for i in range(maturity, -1, -1):
            print(i)
            for j in range(len(stock[:i + 1])):
                if i == maturity:
                    call_value[i,j] = eval(payoff)
                else:
                    call_value[i, j] = (1 / (1 + rate)) * (
                                Martingale[0] * call_value[i + 1, j] + Martingale[1] * call_value[i + 1, j + 1])
                if american:
                    call_value[i, j] = np.maximum(call_value[i, j], eval(payoff))
        return call_value
    if np.isnan(stock[-1,:]).sum() != 0:
        if call:
            payoff = 'np.maximum(stock[j,i] - strike,0)'
        else:
            payoff = 'np.maximum( strike - stock[j,i] ,0)'

        call_value = np.empty_like(stock)
        call_value[:] = np.nan

        for i in range(maturity, -1, -1):

            for j in range(np.argwhere(np.isfinite(stock[:,i]))[0,0], len(stock)+i-maturity):
                print(i,j-1,j,j+1)
                if i == maturity:
                    call_value[j,i] = eval(payoff)
                else:
                    call_value[j,i] = (1 / (1 + rate)) * (
                            Martingale[0] * call_value[j-1,i+1] + Martingale[1] * call_value[j,i+1] + Martingale[2] *
                            call_value[j+1,i+1])
                if american:
                    call_value[j,i] = np.maximum(call_value[j,i], eval(payoff))

        return call_value


