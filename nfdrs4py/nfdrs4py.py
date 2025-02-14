import os
from typing import Union

import numpy as np


class NFDRS4py():
    """Simplified interface object for NFDRS4"""

    def __init__(self,
                 Lat:float=40.,
                 FuelModel:str='W',
                 SlopeClass:int=1,
                 AvgAnnPrecip:float=30.,
                 MCInit1hr:float=0.2,
                 MCInit10hr: float = 0.2,
                 MCInit100hr: float = 0.2,
                 MCInit1000hr: float = 0.2,
                 MCInitLWoody: float = .6,
                 MCInitLHerb: float = .3,
                 LT:bool=True,
                 Cure:bool=True,
                 isAnnual:bool=True,
                 kbdiThreshold:float=100,
                 RegObsHour:int=13,
                 isReinit:bool=False):
        """Initialization function for NFDRS4 object with simplified interface

        Arguments:

        Lat: The latitude of the simulation point (decimal degrees).
        FuelModel: Fuel model character code (V: Grass, W: Grass-Shrub, X: Brush, Y: Timber, Z: Slash).
        SlopeClass: Slope class (1 = <25%, 2 = 26-40%, 3 = 41 - 55%, 4 = 56 - 75%, 5 = 76%+).
        AvgAnnPrecip: Mean annual precipitation (inches).
        MCInit1hr: initial moisture content for 1hr dead fuel,
        MCInit10hr: initial moisture content for 10hr dead fuel
        MCInit100hr: initial moisture content for 100hr dead fuel
        MCInit1000hr: initial moisture content for 1000hr dead fuel
        MCInitLWoody: initial moisture content for live woody fuel
        MCInitLHerb: initial moisture content for live herbaceous fuel
        LT: Use drought fuel load transfer (boolean).
        Cure: Use herbaceous curing (boolean).
        IsAnnual: Treat herbs as annual (boolean).
        kbdiThreshold: Starting KBDI value to begin drought fuel load additions (default 100).
        RegObsHour: Regular observation hour; triggers daily GSI-LFMC calculation (default 13).
        isReinit: If true, indicates re-initialization mid-calculation (not common)."""

        from .nfdrs4_bindings import NFDRS4

        self.nfdrs4 = NFDRS4()
        self.nfdrs4.Init(Lat=Lat,FuelModel=FuelModel,SlopeClass=SlopeClass,AvgAnnPrecip=AvgAnnPrecip,LT=LT, Cure=Cure,
                         isAnnual=isAnnual,kbdiThreshold=kbdiThreshold,RegObsHour=RegObsHour,isReinit=isReinit)

        #self.set_one_hr_params()
        #self.set_ten_hr_params()
        #self.set_hundred_hr_params()
        #self.set_thousand_hr_params()
        #self.set_gsi_params()
        #self.set_herb_gsi_params()
        #self.set_woody_gsi_params()
        #self.set_start_kbdi()
        #self.set_sc_max()
        #self.set_mxd()

        self.set_fuel_moisture(MCInit1hr,MCInit10hr,MCInit100hr,MCInit1000hr,MCInitLWoody,MCInitLHerb)

    def set_from_config(self,config:Union[dict[dict],str])->None:
        """Set NFDRS4py variables from configuration file or dictionary.

        First level keys must be 'general', 'liveFuelMoisture.defaults', 'gsi_opts', 'herb_opts', 'woody_opts',
        'deadFuelMoisture.defaults', '1hr_opts', '10hr_opts', '100hr_opts', '1000hr_opts', and/or 'customFuelModel'
        Second level keys must match variable names in associated nfdrs4py setter
        """
        if type(config) is not dict:
            config = read_config(config)

        self.nfdrs4.Init(config['general']['latitude'],config['general']['fuelmodel'],config['general']['slopeclass'],
                         config['general']['avgannualprecip'],bool(config['general']['useloadtransfer']),
                         bool(config['general']['usecure']),bool(config['general']['isannuals']),
                         config['general']['kbdithreshold'],config['general']['startkbdi'],False)
        if 'customFuelModel' in config.keys():
            self.set_custom_fuel_model(**config['customFuelModel'])
        if '1hr_opts' in config.keys():
            self.set_one_hr_params(**config['1hr_opts'])
        if '10hr_opts' in config.keys():
            self.set_ten_hr_params(**config['10hr_opts'])
        if '100hr_opts' in config.keys():
            self.set_hundred_hr_params(**config['100hr_opts'])
        if '1000hr_opts' in config.keys():
            self.set_thousand_hr_params(**config['1000hr_opts'])
        if 'gsi_opts' in config.keys():
            gsi_opts_reduced = ['gsimax', 'gsiherbgreenup', 'gsitminmin', 'gsitminmax',
                                'gsivpdmin', 'gsivpdmax', 'gsidaylenmin', 'gsidaylenmax',
                                'gsiaveragingdays', 'gsiusevpdavg', 'gsinumprecipdays',
                                'gsirtprecipmin', 'gsirtprecipmax', 'gsiusertprecip']
            gsi_opts_reduced = {k: v for k, v in config['gsi_opts'].items() if k in gsi_opts_reduced}
            self.set_gsi_params(**gsi_opts_reduced)
        if 'herb_opts' in config.keys():
            self.set_herb_gsi_params(**config['herb_opts'])
        if 'woody_opts' in config.keys():
            self.set_woody_gsi_params(**config['woody_opts'])
        if 'kbdi' in config['general'].keys():
            self.set_start_kbdi(config['general'])
        if 'maxsc' in config['general'].keys() and config['general']['maxsc'] > 0:
            self.set_sc_max(config['general']['maxsc'])
        if 'mxd' in config['general'].keys() and config['general']['mxd'] > 0:
            self.set_mxd(config['general']['mxd'])

    def set_custom_fuel_model(self, fuelmodel:str = 'C',
                              description:str = 'Custom',
                              sg1:float = 2000,
                              sg10:float = 109,
                              sg100:float = 30,
                              sg1000:float = 8,
                              sgwood:float = 1500,
                              sgherb:float = 2000,
                              hd:float = 8000,
                              l1:float = 2.5,
                              l10:float = 2,
                              l100:float = 5,
                              l1000:float = 12,
                              lwood:float = .5,
                              lherb:float = .5,
                              depth:float = 1,
                              mxd:float = 25,
                              scm:float = 30,
                              ldrought:float = 0,
                              wndfc:float = .4)->None:
        """Set up and use a custom fuel model for fire danger indices"""

        from .nfdrs4_bindings import CFuelModelParams
        params = CFuelModelParams()
        params.setFuelModel(fuelmodel)
        params.setDescription(description)
        params.setSG1(sg1)
        params.setSG10(sg10)
        params.setSG100(sg100)
        params.setSG1000(sg1000)
        params.setSGWood(sgwood)
        params.setSGHerb(sgherb)
        params.setHD(hd)
        params.setL1(l1)
        params.setL10(l10)
        params.setL100(l100)
        params.setL1000(l1000)
        params.setLWood(lwood)
        params.setLHerb(lherb)
        params.setDepth(depth)
        params.setMXD(mxd)
        params.setSCM(scm)
        params.setLDrought(ldrought)
        params.setWNDFC(wndfc)

        self.nfdrs4.AddCustomFuel(params)
        self.nfdrs4.iSetFuelModel(params.getFuelModel())

    def set_one_hr_params(self, radius:float = .2,
                          adsorptionrate:float = .462252733,
                          maxlocalmoisture:float = .35,
                          stickdensity:float = .4,
                          desorptionrate:float = .06)->None:

        self.nfdrs4.SetOneHourParams(radius,adsorptionrate,maxlocalmoisture,stickdensity,desorptionrate)

    def set_ten_hr_params(self, radius:float = .64,
                          adsorptionrate:float = .079548303,
                          maxlocalmoisture:float = .35,
                          stickdensity:float = .4,
                          desorptionrate:float = .06)->None:

        self.nfdrs4.SetTenHourParams(radius, adsorptionrate, maxlocalmoisture, stickdensity, desorptionrate)

    def set_hundred_hr_params(self, radius:float = 2.0,
                          adsorptionrate:float = .06,
                          maxlocalmoisture:float = .35,
                          stickdensity:float = .4,
                          desorptionrate:float = .06)->None:

        self.nfdrs4.SetHundredHourParams(radius, adsorptionrate, maxlocalmoisture, stickdensity, desorptionrate)

    def set_thousand_hr_params(self, radius:float = 3.81,
                          adsorptionrate:float = .06,
                          maxlocalmoisture:float = .35,
                          stickdensity:float = .4,
                          desorptionrate:float = .06)->None:

        self.nfdrs4.SetHundredHourParams(radius, adsorptionrate, maxlocalmoisture, stickdensity, desorptionrate)

    def set_gsi_params(
        self, gsimax: float = 1, gsiherbgreenup: float = .5, gsitminmin: float = -2.0, gsitminmax: float = 5.0,
        gsivpdmin: float = 900, gsivpdmax: float = 4100, gsidaylenmin: float = 36000, gsidaylenmax: float = 39600,
        gsiaveragingdays: int = 21, gsiusevpdavg: bool = False, gsinumprecipdays: int = 30,
        gsirtprecipmin: float = 0.5, gsirtprecipmax: float = 1.5, gsiusertprecip: bool = False
    ) -> None:
        self.nfdrs4.SetGSIParams(
            gsimax, gsiherbgreenup, gsitminmin, gsitminmax, gsivpdmin, gsivpdmax,
            gsidaylenmin, gsidaylenmax, gsiaveragingdays, bool(gsiusevpdavg), gsinumprecipdays,
            gsirtprecipmin, gsirtprecipmax, bool(gsiusertprecip)
        )

    def set_herb_gsi_params(
        self, gsimax: float = 1, gsiherbgreenup: float = .5, gsitminmin: float = -2.0, gsitminmax: float = 5.0,
        gsivpdmin: float = 900, gsivpdmax: float = 4100, gsidaylenmin: float = 36000, gsidaylenmax: float = 39600,
        gsiaveragingdays: int = 21, gsiusevpdavg: bool = False, gsinumprecipdays: int = 30,
        gsirtprecipmin: float = 0.5, gsirtprecipmax: float = 1.5, gsiusertprecip: bool = False,
        fuelmoisturemin: float = 30.0, fuelmoisturemax: float = 250.0
    ) -> None:
        self.nfdrs4.SetHerbGSIparams(
            gsimax, gsiherbgreenup, gsitminmin, gsitminmax, gsivpdmin, gsivpdmax,
            gsidaylenmin, gsidaylenmax, gsiaveragingdays, bool(gsiusevpdavg), gsinumprecipdays,
            gsirtprecipmin, gsirtprecipmax, bool(gsiusertprecip), fuelmoisturemin, fuelmoisturemax
        )

    def set_woody_gsi_params(
        self, gsimax: float = 1, gsiherbgreenup: float = .5, gsitminmin: float = -2.0, gsitminmax: float = 5.0,
        gsivpdmin: float = 900, gsivpdmax: float = 4100, gsidaylenmin: float = 36000, gsidaylenmax: float = 39600,
        gsiaveragingdays: int = 21, gsiusevpdavg: bool = False, gsinumprecipdays: int = 30,
        gsirtprecipmin: float = 0.5, gsirtprecipmax: float = 1.5, gsiusertprecip: bool = False,
        fuelmoisturemin: float = 60.0, fuelmoisturemax: float = 200.0
    ) -> None:
        self.nfdrs4.SetWoodyGSIparams(
            gsimax, gsiherbgreenup, gsitminmin, gsitminmax, gsivpdmin, gsivpdmax,
            gsidaylenmin, gsidaylenmax, gsiaveragingdays, bool(gsiusevpdavg), gsinumprecipdays,
            gsirtprecipmin, gsirtprecipmax, bool(gsiusertprecip), fuelmoisturemin, fuelmoisturemax
        )

    def set_start_kbdi(self,skbdi=100)->None:
        """Starting drought index"""
        self.nfdrs4.SetStartKBDI(skbdi)

    def set_sc_max(self,maxsc=0)->None:
        """Max spread component? Any positive value other than zero overrides fuel model default."""
        self.nfdrs4.SetSCMax(maxsc)

    def set_mxd(self,mxd=0)->None:
        """Moisture of extinction. Any positive value other than zero overrides fuel model default."""
        self.nfdrs4.SetMXD(mxd)

    def set_fuel_moisture(self,dmc_1hr=.2,dmc_10hr=.2,dmc_100hr=.2,dmc_1000hr=.2,lmc_woody=.6,lmc_herb=.3,fuel_temp_C=-999)->None:
        """Set fuel moisture directly, typically to set initial conditions"""
        self.nfdrs4.OneHourFM.setMoisture(dmc_1hr)
        self.nfdrs4.TenHourFM.setMoisture(dmc_10hr)
        self.nfdrs4.HundredHourFM.setMoisture(dmc_100hr)
        self.nfdrs4.ThousandHourFM.setMoisture(dmc_1000hr)
        self.nfdrs4.MC1 = dmc_1hr
        self.nfdrs4.MC10 = dmc_10hr
        self.nfdrs4.MC100 = dmc_100hr
        self.nfdrs4.MC1000 = dmc_1000hr
        self.nfdrs4.iSetFuelMoistures(dmc_1hr, dmc_10hr, dmc_100hr, dmc_1000hr, lmc_woody*100, lmc_herb*100, fuel_temp_C)

    def update_weather(self,
               Year: int,
               Month: int,
               Day: int,
               Hour: int,
               Temp: float,
               RH: float,
               PPTAmt: float,
               SolarRad: float,
               WS: float,
               SnowDay: bool)->None:
        """Initialize a new timestep by providing new weather data. Units are US customary, time is local.

        Args:
            Year: year of observation (local time, not utc/zulu)
            Month: month of observation (local time, not utc/zulu)
            Day: day of observation (local time, not utc/zulu)
            Hour: hour of observation (local time, not utc/zulu)
            Temp: air temperature, degrees F
            RH: relative humidity, percent, expressed as value between 0 and 100
            PPTAmt: precipitation in this hour, inches
            SolarRad: solar radiation, watts per sq meter
            WS: wind speed, miles per hour
            SnowDay: boolean flag for snow day (check FW21 documentation)
        """

        self.nfdrs4.Update(int(Year),int(Month),int(Day),int(Hour),float(Temp),float(RH),float(PPTAmt),
                           float(SolarRad),float(WS),bool(SnowDay))

    def update_weather_metric(self,
               Year: int,
               Month: int,
               Day: int,
               Hour: int,
               Temp: float,
               RH: float,
               PPTAmt: float,
               SolarRad: float,
               WS_km_hr: float = None,
               WS_m_s: float = None,
               SnowDay: bool=False):
        """Initialize a new timestep by providing new weather data. Units are metric, time is local.

        Args:
            Year: year of observation (local time, not utc/zulu)
            Month: month of observation (local time, not utc/zulu)
            Day: day of observation (local time, not utc/zulu)
            Hour: hour of observation (local time, not utc/zulu)
            Temp: air temperature, degrees C
            RH: relative humidity, percent, expressed as value between 0 and 100
            PPTAmt: precipitation in this hour, cm
            SolarRad: solar radiation, watts per sq meter
            WS_km_hr: wind speed, km per hour. Must be provided if WS_m_s is None.
            WS_m_s: wind speed, meters per second. Must be provided if WS_km_hr is None.
            SnowDay: boolean flag for snow day (check FW21 documentation)
        """
        Temp = Temp * 1.8 + 32
        PPTAmt /= 2.54
        if WS_km_hr is not None:
            WS = WS_km_hr / 1.609344
        elif WS_m_s is not None:
            WS = WS_m_s * 2.2369362921
        else:
            raise ValueError("Either WS_km_hr or WS_m_s must be provided.")

        self.nfdrs4.Update(int(Year),int(Month),int(Day),int(Hour),float(Temp),float(RH),float(PPTAmt),
                           float(SolarRad),float(WS),bool(SnowDay))

    def get_current_fuel_moisture(self)->dict[float]:
        d = {'dmc_1_hr':self.nfdrs4.MC1,
             'dmc_10_hr':self.nfdrs4.MC10,
             'dmc_100_hr':self.nfdrs4.MC100,
             'dmc_1000_hr':self.nfdrs4.MC1000,
             'lmc_herb':self.nfdrs4.MCHERB,
             'lmc_woody':self.nfdrs4.MCWOOD}
        return d

    def get_current_indices(self)->dict[float]:
        d = {'burning_index':self.nfdrs4.BI,
             'energy_release_component':self.nfdrs4.ERC,
             'spread_component':self.nfdrs4.SC,
             'ignition_component':self.nfdrs4.IC,
             'growing_season_index':self.nfdrs4.m_GSI,
             'kb_drought_index':self.nfdrs4.KBDI}
        return d


    def process_df(self,df,
                   datetime_col:Union[int,str]="DateTime",
                   temp_col:Union[int,str]="Temperature(F)",
                   rh_col:Union[int,str]="RelativeHumidity(%)",
                   precip_col:Union[int,str]="Precipitation(in)",
                   srad_col:Union[int,str]="SolarRadiation(W/m2)",
                   windspeed_col:Union[int,str]="WindSpeed(mph)",
                   snowflag_col:Union[int,str]="SnowFlag")->'pd.DataFrame':

        """Process a dataframe or array containing weather data, e.g. in FW21 format.

        Specify column name (str) or position (int) for each required weather variable.

        Required columns:
            Year: year of observation (local time, not utc/zulu)
            Month: month of observation (local time, not utc/zulu)
            Day: day of observation (local time, not utc/zulu)
            Hour: hour of observation (local time, not utc/zulu)
            Temp: air temperature, degrees F
            RH: relative humidity, percent, expressed as value between 0 and 100
            PPTAmt: precipitation in this hour, inches
            SolarRad: solar radiation, watts per sq meter
            WS: wind speed, miles per hour
            SnowDay: boolean flag for snow day (check FW21 documentation)"""

        import pandas as pd
        import numpy as np

        try:
            dt_series = pd.to_datetime(df.iloc[:, datetime_col])
        except:
            dt_series = pd.to_datetime(df[datetime_col])

        try:
            wx = df.iloc[:, [temp_col, rh_col, precip_col, srad_col, windspeed_col, snowflag_col]]
        except:
            wx = df[[temp_col, rh_col, precip_col, srad_col, windspeed_col, snowflag_col]]

        try:
            try:
                wx_arr = wx.to_numpy()
            except:
                wx_arr = wx.to_array()
        except:
            wx_arr = np.array(wx)

        dt_arr = np.stack([
            dt_series.dt.year,
            dt_series.dt.month,
            dt_series.dt.day,
            dt_series.dt.hour,
        ]).T

        if not ((wx_arr.shape[0]==df.shape[0]) and (wx_arr.shape[1]==6) and
                (dt_arr.shape[0]==df.shape[0]) and (dt_arr.shape[1]==4)):
            raise TypeError("Could not cast input table to numpy arrays. Try casting to pandas.DataFrame first.")



        results_cols = ['dmc_1_hr', 'dmc_10_hr', 'dmc_100_hr', 'dmc_1000_hr', 'lmc_herb', 'lmc_woody',
                        'burning_index', 'energy_release_component', 'spread_component', 'ignition_component',
                        'growing_season_index','kb_drought_index']

        results = np.zeros([wx_arr.shape[0],len(results_cols)],float)

        for i in range(wx_arr.shape[0]):
            self.update_weather(dt_arr[i, 0], dt_arr[i, 1], dt_arr[i, 2], dt_arr[i, 3], wx_arr[i, 0], wx_arr[i, 1],
                                wx_arr[i, 2], wx_arr[i, 3], wx_arr[i, 4], wx_arr[i,5])

            results[i, :] = [self.nfdrs4.MC1/100, self.nfdrs4.MC10/100, self.nfdrs4.MC100/100, self.nfdrs4.MC1000/100,
                             self.nfdrs4.MCHERB/100, self.nfdrs4.MCWOOD/100,
                             self.nfdrs4.BI, self.nfdrs4.ERC, self.nfdrs4.SC, self.nfdrs4.IC,
                             self.nfdrs4.m_GSI,self.nfdrs4.KBDI]

        results = pd.DataFrame(results,columns=results_cols)

        return pd.concat([df,results],axis=1)

    @classmethod
    def init_from_config(cls, config: Union[dict[dict],str]):
        """Initialize NFDRS4py interface from configuration file or dictionary.

        First level keys must be 'general', 'liveFuelMoisture.defaults', 'gsi_opts', 'herb_opts', 'woody_opts',
        'deadFuelMoisture.defaults', '1hr_opts', '10hr_opts', '100hr_opts', '1000hr_opts', and/or 'customFuelModel'
        Second level keys must match variable names in associated nfdrs4py setter"""

        interface = cls()
        interface.set_from_config(config)
        return interface

def read_config(fp)->dict[dict]:
    """Read config file to dictionary. Must be formatted as nfdrs4 config or as .ini.

    Option names must match variable names of associated variables used in nfdrs4py setters. If format is .ini, sections
    must be 'general', 'liveFuelMoisture.defaults', 'gsi_opts', 'herb_opts', 'woody_opts', 'deadFuelMoisture.defaults',
    '1hr_opts', '10hr_opts', '100hr_opts', '1000hr_opts', and/or 'customFuelModel'"""

    import configparser
    import ast

    # Read text file, add initial section if needed, convert dictionaries and @copyFrom commands to be .ini friendly.
    lines = []
    with open(fp, encoding='utf8') as f:
        line = f.readline()
        if '[' not in line:
            lines.append('[general]\n')
        while line:
            if '{' in line:
                split = line.split('{')
                section = split[0].strip()
                lines.append(f'[{section}]\n')
                if len(split) > 0:
                    line = ' '.join(split[1:])
            line = line.replace('}', '')
            line = line.replace('@copyFrom', f'@copyFrom = ')
            lines.append(line)
            line = f.readline()

    # Send to configparser
    run_config = configparser.ConfigParser()
    run_config.read_string(''.join(lines))

    # Convert to dictionary
    d = {}
    for section in run_config.keys():
        d[section] = {}
        # Copy all key/value pairs from another section
        if '@copyfrom' in run_config[section].keys():
            copyfrom = run_config[section]['@copyfrom'].strip('\";\'')
            for item in d[copyfrom].items():
                d[section][item[0]] = item[1]

        for option in run_config[section].keys():
            if not '@copy' in option:
                # Clean and parse each value
                val = run_config[section][option]
                if type(val) is str:
                    val = val.replace('\"', '').replace(';', '').replace('\'', '')
                    vl = val.lower()
                    if vl == 'true' or vl == 't':
                        val = True
                    elif vl == 'false' or vl == 'f':
                        val = False
                    else:
                        try:
                            val = ast.literal_eval(val)
                        except (ValueError, SyntaxError):
                            val = str(val)

                d[section][option] = val

    return d
