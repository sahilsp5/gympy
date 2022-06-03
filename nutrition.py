''' Observe your food intake for just one meal or whole day eating

(For calculations purpose only)
'''

from typing import Union
import warnings
import pandas as pd


food_cols = \
    ['food'           ,'energy'   ,'carbs'    ,'protein'    ,'fat'  ,'price']
# units used - energy : kcal, carbs : gram, protein : gram, fat : gram, price : rupee
food_data = [ # NOTE : sample food data per 100g. (according as cols above)
    ['milk'           ,58.2       ,4.8        ,3            ,3      ,6.36   ],
    ['oats'           ,379        ,67.8       ,11.6         ,9      ,15.13  ],
    ['banana'         ,89         ,23         ,1.1          ,0.3    ,3.7    ],
    ['peanut butter'  ,612.5      ,19         ,26           ,49     ,34.9   ],
    ['curd'           ,75         ,5          ,3.7          ,4.5    ,9      ],
    ['egg'            ,155        ,1.1        ,13           ,11     ,10.66  ],
    ['whey isolate'   ,366.3      ,1.66       ,90           ,1      ,210    ],
    ['soya granules'  ,354.1      ,33.5       ,53.2         ,0.82   ,30     ],
    ['paneer'         ,296        ,4.5        ,20           ,22     ,32     ],
    ['rice'           ,344        ,77         ,6.7          ,0.5    ,9.8    ],
    ['almond'         ,194        ,2          ,7            ,17     ,80     ],
    ['ghee'           ,897        ,0          ,0            ,99.7   ,65     ],
    # -- more additions here --
]


foodf = pd.DataFrame(food_data, columns=food_cols) # food df
foodf.set_index('food', inplace=True)
foodf.sort_index(inplace=True)


def macro_perRupee(macro:str):
    ''' Calculate macro per rupee (most efficient food or value for money in given macro)

        `macro` : macro type, must be one of ['energy', 'carbs', 'protein', 'fat']

        How to read Result:
            food 'x' provides 'y' grams of given macro in 1 rupee
            where x will be series index and y will be respective value as float

        Example
        ---
            >>> print( macro_perRupee('protein') )
    '''
    if not isinstance(macro, str) : raise TypeError(f'macro must be of type <str>.  got {type(macro)}')
    macros_av = ['energy', 'carbs', 'protein', 'fat'] # macros available
    if macro not in macros_av : raise ValueError(f'Invalid macro - {macro}')
    result = (foodf[macro] / foodf['price']) # per 100g. will get cut (being in both num n denom) to give unit as gram (or kcal) per rupee
    result.name = f'{macro}_per_rupee'
    return result.sort_values(ascending=False)


class Stats:
    ''' Calculate stats for the consumption of food

        Parameters
        ---
            `consumption`: consumption of food (in grams)
                eg. -> {'milk':500, 'oats':40, 'banana':200}
    '''

    def __init__(self, consumption:Union[dict, pd.Series]):
        if not isinstance(consumption, (dict, pd.Series)) : raise TypeError(f'consumption must be of type <(dict, pd.Series)>.  got {type(consumption)}')
        self.consumption_sr = pd.Series(consumption)
        unav_food = self.consumption_sr.index.difference(foodf.index).tolist() # unavailable food
        if len(unav_food) > 0 : warnings.warn(f"Food : {unav_food} has no data available and {'it' if len(unav_food) == 1 else 'they'} will be discarded in calculations.", UserWarning)

        self.consumption_df = (foodf / 100).multiply(self.consumption_sr, axis=0) # as foodf shows per 100g. data ... calculating it per g. and multiplying with respective food consumption

        self.emp_sr = self.consumption_df.sum(axis=0) # energy, macro and pricing series (net sum)
        self.macro_sr = self.emp_sr[['carbs', 'protein', 'fat']] # macro series
        self.mpb_sr = (self.macro_sr / self.macro_sr.sum(axis=0)) * 100 # macro percent breakup series


    def stats_breakup(self):
        ''' stats breakup for each of the food separately '''
        return self.consumption_df.dropna()

    def consolidated_stats(self):
        ''' consolidated stats (net sum of features for all food combined) '''
        return self.emp_sr

    def macro_breakup(self):
        ''' main macros percent breakup (i.e. % of carb, protein n fat taken) '''
        return self.mpb_sr


def test_run():
    print('\nTest run for "(bulking) Oat Smoothie"\n---------------------------\n\n')

    ingredients = {'milk':500, 'oats':40, 'banana':100, 'almond':25, 'whey isolate':30, 'peanut butter':30} # ingredients used (in grams)
    foostat = Stats(consumption=ingredients) # food stats object

    print('● Consolidated stats for meal:\n\n', foostat.consolidated_stats(), '\n\n', sep='')

    print('● Macro Breakup (in %):\n\n', foostat.macro_breakup(), '\n\n', sep='')

    print('● Stats for each ingredient:\n\n', foostat.stats_breakup(), '\n\n', sep='')


if __name__ == '__main__':    
    test_run()
