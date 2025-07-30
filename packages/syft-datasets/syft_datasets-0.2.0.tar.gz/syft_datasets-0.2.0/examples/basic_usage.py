#!/usr/bin/env python3
"""Basic usage examples for syft-datasets package."""

import syft_datasets as syd


def main():
    """Run basic usage examples."""
    print("🚀 Syft-Datasets Basic Usage Examples")
    print("=" * 40)

    # Example 1: Basic dataset access
    print("\n📊 1. Accessing all datasets:")
    try:
        print(f"Total datasets found: {len(syd.datasets)}")

        if len(syd.datasets) > 0:
            print(f"First dataset: {syd.datasets[0]}")
            print(f"Dataset URL: {syd.datasets[0].syft_url}")
        else:
            print(
                "No datasets found. Make sure SyftBox is running and you have access to datasites."
            )

    except Exception as e:
        print(f"Error accessing datasets: {e}")
        print("Make sure SyftBox is properly installed and configured.")

    # Example 2: Searching datasets
    print("\n🔍 2. Searching for datasets:")
    try:
        # Search for datasets with 'data' in the name
        search_results = syd.datasets.search("data")
        print(f"Datasets containing 'data': {len(search_results)}")

        for i, dataset in enumerate(search_results[:3]):  # Show first 3
            print(f"  {i + 1}. {dataset.name} from {dataset.email}")

    except Exception as e:
        print(f"Error searching datasets: {e}")

    # Example 3: Filtering by email
    print("\n📧 3. Filtering by email:")
    try:
        # Get unique emails first
        emails = syd.datasets.list_unique_emails()
        print(f"Available emails: {emails}")

        if emails:
            # Filter by first email domain
            domain = emails[0].split("@")[1] if "@" in emails[0] else emails[0]
            filtered = syd.datasets.filter_by_email(domain)
            print(f"Datasets from {domain}: {len(filtered)}")

    except Exception as e:
        print(f"Error filtering datasets: {e}")

    # Example 4: Dataset selection
    print("\n✅ 4. Dataset selection examples:")
    try:
        if len(syd.datasets) > 0:
            # Select by index
            first_dataset = syd.datasets[0]
            print(f"First dataset: {first_dataset}")

            # Select multiple by slicing
            if len(syd.datasets) >= 3:
                first_three = syd.datasets[:3]
                print(f"First three datasets: {len(first_three)} datasets")

            # Select by specific indices
            if len(syd.datasets) >= 2:
                selected = syd.datasets.get_by_indices([0, 1])
                print(f"Selected specific datasets: {len(selected)} datasets")

    except Exception as e:
        print(f"Error with dataset selection: {e}")

    # Example 5: Getting help
    print("\n❓ 5. Getting help:")
    print("To see all available methods and examples, run:")
    print("syd.datasets.help()")

    print("\n🎉 Examples completed!")
    print("\nTo see the interactive UI in Jupyter, try:")
    print("import syft_datasets as syd")
    print("syd.datasets  # This will show the beautiful HTML interface")


if __name__ == "__main__":
    main()
