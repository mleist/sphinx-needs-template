# reqif/public/

Sample ReqIF files shipped with the template, useful as round-trip targets
for `reqif-bridge`.

| File                  | Notes                                                |
| --------------------- | ---------------------------------------------------- |
| `garden_sample.reqif` | The full set of demo needs exported via the bridge. |

## Round-trip

```bash
# Re-import the sample as a JSON list of need dicts
reqif-bridge import reqif/public/garden_sample.reqif -o /tmp/needs.json

# Build needs.json fresh and re-export
make needs
make reqif-export
```
