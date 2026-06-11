# ShipPipe — Marine Piping System Designer

A Python + Streamlit web app for designing marine piping systems — pipe sizing, pump specification, BOM generation, and Excel/PDF export.

**Live App:** https://pipe.sujikumar.com  
**Built by:** [Suji Kumar C](https://sujikumar.com) — Marine Software Engineer

## Systems Covered

| System | Fluid | Velocity Range |
|--------|-------|---------------|
| Ballast | Sea Water | 1.5 – 3.0 m/s |
| Bilge | Sea Water | 1.0 – 2.5 m/s |
| Fuel Oil HFO | Heavy Fuel Oil | 0.5 – 1.0 m/s |
| Fuel Oil MDO | Marine Diesel Oil | 0.8 – 1.5 m/s |
| Fire & GS | Sea Water | 3.0 – 5.0 m/s |
| Fresh Water | Fresh Water | 1.0 – 2.5 m/s |
| Cooling SW | Sea Water | 1.5 – 3.0 m/s |
| Cooling FW | Fresh Water | 1.0 – 2.5 m/s |

## Features

- Pipe sizing per ASME B36.10 (SCH 40 / 80 / 160)
- Flow velocity, Reynolds number, Darcy-Weisbach pressure drop
- Pump head, motor power (kW), NPSH check
- Complete Bill of Materials per system
- Excel + PDF spec sheet export
- Dark/light theme (Streamlit built-in)

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set `app.py` as entry point
4. Deploy

## Engineering References

- Pipe schedules: ASME B36.10M
- Pressure drop: Darcy-Weisbach equation + Colebrook-White friction factor
- Fire system: SOLAS II-2 requirements
- Fuel oil piping: SOLAS II-2 Reg. 4 (flanged joints in machinery spaces)
