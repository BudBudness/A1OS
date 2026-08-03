# A1OS Product Factory v1.1

Generate products:

python3 generate_product.py <product-name>

Example:

python3 generate_product.py media-os

Generated structure:

products/
└── product-name/
    ├── core/
    ├── intelligence/
    ├── api/
    ├── web/
    ├── deployments/
    └── docs/

Each product receives:
- A1OS metadata
- Core modules
- Standard layers
