# Modeling Soil Moisture Trends in Lethbridge, Alberta Using a 0D Water-Balance Approach

## Background

The Canadian Prairies are a vital ecoregion for the country, and hydrological changes can have substantial effects on the economy and environment (Hanesiak et al., 2011, Selby, Loring & Baulch, 2025). As global climate change continues to alter soil moisture dynamics in the region (Chipanshi et al., 2021), identifying soil moisture trends is important for determining the risks to agricultural productivity and ecosystem health. 

In particular, Lethbridge, Alberta is an area of interest because it lies within Palliser’s Triangle, a semi-arid region historically seen as unsuitable for agriculture. However, this area is now a critical location for Canada’s agricultural sector due to irrigation practices (Lemmen et al., 1998). The intersection of climatic change and water management strategies makes Lethbridge an ideal location for modelling soil moisture dynamics and assessing how these interacting forces impact agricultural potential and ecosystem resilience.

The goal of this project is to use the Government of Alberta’s Soil Group Map (2015) and the Alberta Climate Services (ACIS) database to obtain soil texture and meteorological data from the Lethbridge weather station, in order to model daily soil moisture trends over time (Government of Aberta, 2026).

## Model Description

The proposed model is a 0D bucket model of soil moisture based on the mass balance equation described by Rodriguez-Iturbe et al. (1999). It is a simplified process-based model that will take historical data and estimate evapotranspiration and drainage processes to determine soil moisture trends over time. As the input data will be daily weather aggregates from the Lethbridge weather station, the model will only be representative of the area surrounding the weather station itself. Additionally, this model does not take into consideration lateral movement of water through soil, and so will estimate general trends of soil moisture, rather than being spatially precise.

$$
S_{t+1} = S_t + P_t - ET_t - D_t
$$

S<sub>t</sub> represents soil water storage at one day in mm. The initial value of St will be estimated using observed soil moisture data for the region, if available, or a value based on soil texture and calculated field capacity. P<sub>t</sub> represents the total precipitation for that day and E<sub>t</sub> represents the evapotranspiration for that day, approximated by Hargreaves equation (Hargreaves & Samani, 1982): 

$$
ET_0 = 0.0023 \cdot (T_{\text{mean}} + 17.8) \cdot \sqrt{T_{\text{max}} - T_{\text{min}}}
$$


D<sub>t</sub> represents the drainage of the soil, where the surface will be represented as having a fixed capacity for holding water (Manabe, 1969). D<sub>t</sub> is outlined below, where S<sub>FC</sub> represents field capacity or the maximum capacity for water at the site and k is the drainage coefficient determined by soil texture.

$$
D_t =
\begin{cases}
k \cdot (S_t - SFC) & \text{if } S_t > S_{FC},\\\\[4pt]
0 & \text{if } S_t \le S_{FC}
\end{cases}
$$

Finally, S<sub>FC</sub> will be a constant inferred by the soil texture and root zone depth in meters. Since soil water storage is reported in mm, it will be converted by multiplying by 1000.

$$
S_{FC} = \theta_{FC} \cdot Z_{1000}
$$

𝛳<sub>FC</sub>, or field capacity, will be taken from Saxton and Rawls estimates based on soil texture (2006), and root zone depth, Z, will be estimated based on root survey data for Lethbridge that has not yet been sourced.

The model’s output will be daily soil water storage (mm) and its performance will be assessed using data from the Agriculture and Agri-Food Canada Satellite Soil Moisture database that reports soil moisture in the top 5cm of soil across Canada (2025). Since the proposed model represents the entire root zone, validation will focus on assessing general trend agreement rather than exact values.

## Conclusion

This project will result in a model and accompanying graphical user interface (GUI) that takes input data to estimate daily soil moisture and visualize long-term trends. Such results can be used to identify changes in climate or management that affect soil moisture in the area and may have an impact on the surrounding agricultural potential and ecosystem dynamics over time.

## References
Agriculture and Agri-Food Canada. (2025). Satellite Soil Moisture. Agriculture.canada.ca. https://agriculture.canada.ca/en/agricultural-production/weather/satellite-soil-moisture

Chipanshi, A., Berry, M., Zhang, Y., Qian, B., & Steier, G. (2021). Agroclimatic indices across the Canadian Prairies under a changing climate and their implications for agriculture. International Journal of Climatology, 42(4), 2351–2367. https://doi.org/10.1002/joc.7369

Government of Alberta. (2015). Soil Group Map of Alberta. Agric.gov.ab.ca; Government of Alberta. https://www1.agric.gov.ab.ca/soils/soils.nsf/soilgroupmap

Government of Alberta. (2026). Current and Historical Alberta Weather Station Data Viewer. Acis.alberta.ca; Government of Alberta. https://acis.alberta.ca/weather-data-viewer.jsp

Hanesiak, J. M., Stewart, R. E., Bonsal, B. R., Harder, P., Lawford, R., Aider, R., Amiro, B. D., Atallah, E., Barr, A. G., Black, T. A., Bullock, P., Brimelow, J. C., Brown, R., Carmichael, H., Derksen, C., Flanagan, L. B., Gachon, P., Greene, H., Gyakum, J., & Henson, W. (2011). Characterization and Summary of the 1999–2005 Canadian Prairie Drought. Atmosphere-Ocean, 49(4), 421–452. https://doi.org/10.1080/07055900.2011.626757

Hargreaves, G. H., & Samani, Z. A. (1982). Estimating potential evapotranspiration. Journal of Irrigation and Drainage Engineering, 108, 223–230.

Lemmen, D. S., Vance, R. E., Campbell, I. A., David, P. P., Pennock, D. J., Sauchyn, D. J., & Wolfe, S. A. (1998). Geomorphic systems of the Palliser Triangle, southern Canadian Prairies: description and response to changing climate (p. 52). Natural Resources Canada. https://doi.org/10.4095/210076

Manabe, S. (1969). Climate and the ocean circulation. 1. The atmospheric circulation and the hydrology of the Earth’s surface. Monthly Weather Review, 97(11), 739–774. https://doi.org/10.1175/1520-0493(1969)097%3C0739:CATOC%3E2.3.CO;2

Rodriguez-Iturbe, I., Porporato, A., Ridolfi, L., Isham, V., & Cox, D. R. (1999). Probabilistic Modelling of Water Balance at a Point: The Role of Climate, Soil and Vegetation. Proceedings: Mathematical, Physical and Engineering Sciences, 455(1990), 3789–3805. JSTOR. https://doi.org/10.2307/53509

Saxton, K. E., & Rawls, W. J. (2006). Soil Water Characteristic Estimates by Texture and Organic Matter for Hydrologic Solutions. Soil Science Society of America Journal, 70(5), 1569. https://doi.org/10.2136/sssaj2005.0117

Selby, D., Loring, P. A., & Baulch, H. M. (2025). The future Prairie Pothole Region: scenarios of change. FACETS, 10, 1–12. https://doi.org/10.1139/facets-2024-0278