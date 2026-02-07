# Final Comprehensive Evaluation Results

## Configuration

- **Nodes**: 100
- **Initial Energy**: 0.2J
- **Max Rounds**: 500
- **Traffic**: 3 packets/round

## Results Summary

| Algorithm | FND | HND | LND | PDR (%) | Efficiency (pkt/J) | Packets Delivered |
|-----------|-----|-----|-----|---------|-------------------|------------------|
| LEACH | N/A | N/A | 500 | 100.00 | 1506.90 | 1500/1500 |
| PEGASIS | N/A | N/A | 500 | 100.00 | 265.75 | 511/511 |
| OSPF | N/A | N/A | 500 | 100.00 | 2017.91 | 1500/1500 |
| NN_ILEACH | N/A | N/A | 500 | 100.00 | 1451.97 | 1500/1500 |
| DOS_RL | N/A | N/A | 500 | 100.00 | 566.90 | 48/48 |

## Key Observations

- **Best PDR**: LEACH (100.00%)
- **Best Energy Efficiency**: OSPF (2017.91 pkt/J)
