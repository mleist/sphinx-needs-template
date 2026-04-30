# reqif/private/

Drop your **private ReqIF imports / exports** here. Files in this folder
are ignored by git.

Round-trip examples:

```bash
# Import a customer-supplied .reqif into a JSON working set
reqif-bridge import reqif/private/customer.reqif \
                    -o docs/private/_imported_needs.json

# Export the current sphinx-needs state back as ReqIF
reqif-bridge export docs/public/_build/needs/needs.json \
                    -o reqif/private/garden.reqif
```
