import os
from typing import List

import pandas as pd
from syft_core import Client
from syft_rds import init_session
from tabulate import tabulate

__version__ = "0.1.0"


class Dataset:
    """Represents a dataset from a specific datasite"""

    def __init__(self, email: str, dataset_name: str, dataset_obj=None):
        self.email = email
        self.name = dataset_name
        self.dataset_obj = dataset_obj
        self._syft_url = f"syft://{email}/private/datasets/{dataset_name}"

    def __str__(self):
        return f"Dataset(email='{self.email}', name='{self.name}')"

    def __repr__(self):
        return self.__str__()

    @property
    def syft_url(self):
        return self._syft_url


class DatasetCollection:
    """Collection of datasets that can be indexed and displayed as a table"""

    def __init__(self, datasets=None, search_info=None):
        if datasets is None:
            self._datasets = []
            self._search_info = None
            self._load_datasets()
        else:
            self._datasets = datasets
            self._search_info = search_info

    def _load_datasets(self):
        """Load all available datasets from connected datasites"""
        try:
            client = Client.load()

            # Check 1: Verify SyftBox filesystem is accessible (works offline)
            filesystem_ok = False
            try:
                datasites = list(map(lambda x: x.name, client.datasites.iterdir()))
                filesystem_ok = True
                print(f"✅ SyftBox filesystem accessible — logged in as: {client.email}")
            except Exception as e:
                print(f"❌ SyftBox filesystem not accessible: {e}")
                print("    Make sure SyftBox is properly installed")

            # Check 2: Verify SyftBox app is actually running (HTTP endpoint check)
            try:
                import requests

                response = requests.get(str(client.config.client_url), timeout=2)
                if response.status_code == 200 and "go1." in response.text:
                    print(f"✅ SyftBox app running at {client.config.client_url}")
            except Exception:
                print(f"❌ SyftBox app not running at {client.config.client_url}")

            # Return early if filesystem not accessible
            if not filesystem_ok:
                return

            for email in datasites:
                try:
                    datasite_client = init_session(host=email)
                    for ds in datasite_client.datasets:
                        dataset = Dataset(email=email, dataset_name=ds.name, dataset_obj=ds)
                        self._datasets.append(dataset)
                except Exception:
                    # Skip datasites that can't be accessed
                    continue

        except Exception as e:
            print(f"⚠️  Could not find SyftBox client: {e}")
            print("    Make sure SyftBox is installed and you're logged in")

    def search(self, keyword):
        """Search for datasets containing the keyword in name or email

        Args:
            keyword: Search term to look for in dataset name or email

        Returns:
            DatasetCollection: New collection with filtered datasets
        """
        keyword = keyword.lower()
        filtered_datasets = []

        for dataset in self._datasets:
            if keyword in dataset.name.lower() or keyword in dataset.email.lower():
                filtered_datasets.append(dataset)

        search_info = f"Search results for '{keyword}'"
        return DatasetCollection(datasets=filtered_datasets, search_info=search_info)

    def filter_by_email(self, email_pattern):
        """Filter datasets by email pattern

        Args:
            email_pattern: Pattern to match in email (case insensitive)

        Returns:
            DatasetCollection: New collection with filtered datasets
        """
        pattern = email_pattern.lower()
        filtered_datasets = []

        for dataset in self._datasets:
            if pattern in dataset.email.lower():
                filtered_datasets.append(dataset)

        search_info = f"Filtered by email containing '{email_pattern}'"
        return DatasetCollection(datasets=filtered_datasets, search_info=search_info)

    def list_unique_emails(self):
        """Get list of unique email addresses"""
        emails = set(dataset.email for dataset in self._datasets)
        return sorted(list(emails))

    def list_unique_names(self):
        """Get list of unique dataset names"""
        names = set(dataset.name for dataset in self._datasets)
        return sorted(list(names))

    def to_list(self):
        """Convert to a simple list of datasets for model parameter"""
        return list(self._datasets)

    def get_by_indices(self, indices):
        """Get datasets by list of indices

        Args:
            indices: List of indices to select

        Returns:
            List[Dataset]: Selected datasets
        """
        return [self._datasets[i] for i in indices if 0 <= i < len(self._datasets)]

    def help(self):
        """Show help and examples for using the dataset collection"""
        help_text = """
🔍 Dataset Collection Help

Interactive UI:
  nsai.datasets              # Show interactive table with search & selection
  • Use search box to filter in real-time
  • Check boxes to select datasets  
  • Click "Generate Code" for copy-paste Python code

Programmatic Usage:
  nsai.datasets[0]           # Get first dataset
  nsai.datasets[:3]          # Get first 3 datasets
  len(nsai.datasets)         # Count datasets

Search & Filter:
  nsai.datasets.search("crop")           # Search for 'crop' in names/emails
  nsai.datasets.filter_by_email("andrew") # Filter by email containing 'andrew'
  nsai.datasets.get_by_indices([0,1,5])  # Get specific datasets by index
  
Utility Methods:
  nsai.datasets.list_unique_emails()     # List all unique emails
  nsai.datasets.list_unique_names()      # List all unique dataset names
  
Usage in Model:
  crop_datasets = nsai.datasets.search("crop")
  response = nsai.client.chat.completions.create(
      model=crop_datasets[:3],  # First 3 results
      messages=[...]
  )
        """
        print(help_text)

    def __getitem__(self, index):
        """Allow indexing like datasets[0] or slicing like datasets[:3]"""
        if isinstance(index, slice):
            slice_info = f"{self._search_info} (slice {index})" if self._search_info else None
            return DatasetCollection(datasets=self._datasets[index], search_info=slice_info)
        return self._datasets[index]

    def __len__(self):
        return len(self._datasets)

    def __iter__(self):
        return iter(self._datasets)

    def _repr_html_(self):
        """HTML representation for Jupyter notebooks"""
        if not self._datasets:
            return "<p><em>No datasets available</em></p>"

        title = self._search_info if self._search_info else "Available Datasets"
        count = len(self._datasets)
        search_indicator = (
            f"<p style='color: #28a745; font-style: italic;'>🔍 {self._search_info}</p>"
            if self._search_info
            else ""
        )

        container_id = f"nsai-container-{hash(str(self._datasets)) % 10000}"

        html = f"""
        <style>
        .nsai-container {{
            max-height: 500px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin: 10px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .nsai-header {{
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            margin: 0;
        }}
        .nsai-controls {{
            padding: 10px 15px;
            background-color: #fff;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .nsai-search-box {{
            flex: 1;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 12px;
        }}
        .nsai-btn {{
            padding: 6px 12px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            text-decoration: none;
        }}
        .nsai-btn:hover {{
            background-color: #0056b3;
        }}
        .nsai-btn-secondary {{
            background-color: #6c757d;
        }}
        .nsai-btn-secondary:hover {{
            background-color: #545b62;
        }}
        .nsai-table-container {{
            max-height: 320px;
            overflow-y: auto;
        }}
        .nsai-datasets-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 11px;
            margin: 0;
        }}
        .nsai-datasets-table th {{
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            padding: 6px 8px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .nsai-datasets-table td {{
            border-bottom: 1px solid #f1f3f4;
            padding: 4px 8px;
            vertical-align: top;
        }}
        .nsai-datasets-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .nsai-datasets-table tr.nsai-selected {{
            background-color: #e3f2fd;
        }}
        .nsai-email {{
            color: #0066cc;
            font-weight: 500;
            font-size: 10px;
        }}
        .nsai-dataset-name {{
            color: #28a745;
            font-weight: 500;
            max-width: 180px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .nsai-syft-url {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 9px;
            color: #6c757d;
            max-width: 250px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .nsai-index {{
            text-align: center;
            font-weight: 600;
            color: #495057;
            background-color: #f8f9fa;
            width: 30px;
        }}
        .nsai-checkbox {{
            width: 30px;
            text-align: center;
        }}
        .nsai-output {{
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 10px;
            color: #495057;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        .nsai-status {{
            padding: 5px 15px;
            background-color: #e9ecef;
            font-size: 10px;
            color: #6c757d;
        }}
        </style>
        <div class="nsai-container" id="{container_id}">
            <div class="nsai-header">
                <strong>📊 {title} ({count} total)</strong>
                {search_indicator}
            </div>
            <div class="nsai-controls">
                <input type="text" class="nsai-search-box" placeholder="🔍 Search datasets..." 
                       onkeyup="filterDatasets('{container_id}')">
                <button class="nsai-btn" onclick="selectAll('{container_id}')">Select All</button>
                <button class="nsai-btn nsai-btn-secondary" onclick="clearAll('{container_id}')">Clear</button>
                <button class="nsai-btn" onclick="generateCode('{container_id}')">Generate Code</button>
            </div>
            <div class="nsai-table-container">
                <table class="nsai-datasets-table">
                    <thead>
                        <tr>
                            <th>☑</th>
                            <th>#</th>
                            <th>Email</th>
                            <th>Dataset Name</th>
                            <th>Syft URL</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for i, dataset in enumerate(self._datasets):
            html += f"""
            <tr data-email="{dataset.email.lower()}" data-name="{dataset.name.lower()}" data-index="{i}">
                <td class="nsai-checkbox">
                    <input type="checkbox" onchange="updateSelection('{container_id}')">
                </td>
                <td class="nsai-index">{i}</td>
                <td class="nsai-email">{dataset.email}</td>
                <td class="nsai-dataset-name" title="{dataset.name}">{dataset.name}</td>
                <td class="nsai-syft-url" title="{dataset.syft_url}">{dataset.syft_url}</td>
            </tr>
            """

        html += f"""
                    </tbody>
                </table>
            </div>
            <div class="nsai-status" id="{container_id}-status">
                0 datasets selected • Use checkboxes to select datasets
            </div>
            <div class="nsai-output" id="{container_id}-output" style="display: none;">
                # Copy this code to your notebook:
            </div>
        </div>
        
        <script>
        function filterDatasets(containerId) {{
            const searchBox = document.querySelector(`#${{containerId}} .nsai-search-box`);
            const table = document.querySelector(`#${{containerId}} .nsai-datasets-table tbody`);
            const rows = table.querySelectorAll('tr');
            const searchTerm = searchBox.value.toLowerCase();
            
            let visibleCount = 0;
            rows.forEach(row => {{
                const email = row.dataset.email || '';
                const name = row.dataset.name || '';
                const isVisible = email.includes(searchTerm) || name.includes(searchTerm);
                row.style.display = isVisible ? '' : 'none';
                if (isVisible) visibleCount++;
            }});
            
            updateSelection(containerId);
        }}
        
        function selectAll(containerId) {{
            const table = document.querySelector(`#${{containerId}} .nsai-datasets-table tbody`);
            const checkboxes = table.querySelectorAll('input[type="checkbox"]');
            const visibleCheckboxes = Array.from(checkboxes).filter(cb => 
                cb.closest('tr').style.display !== 'none'
            );
            
            const allChecked = visibleCheckboxes.every(cb => cb.checked);
            visibleCheckboxes.forEach(cb => cb.checked = !allChecked);
            
            updateSelection(containerId);
        }}
        
        function clearAll(containerId) {{
            const table = document.querySelector(`#${{containerId}} .nsai-datasets-table tbody`);
            const checkboxes = table.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = false);
            updateSelection(containerId);
        }}
        
        function updateSelection(containerId) {{
            const table = document.querySelector(`#${{containerId}} .nsai-datasets-table tbody`);
            const rows = table.querySelectorAll('tr');
            const status = document.querySelector(`#${{containerId}}-status`);
            
            let selectedCount = 0;
            rows.forEach(row => {{
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox && checkbox.checked) {{
                    row.classList.add('nsai-selected');
                    selectedCount++;
                }} else {{
                    row.classList.remove('nsai-selected');
                }}
            }});
            
            const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
            status.textContent = `${{selectedCount}} dataset(s) selected • ${{visibleRows.length}} visible`;
        }}
        
        function generateCode(containerId) {{
            const table = document.querySelector(`#${{containerId}} .nsai-datasets-table tbody`);
            const rows = table.querySelectorAll('tr');
            const output = document.querySelector(`#${{containerId}}-output`);
            
            const selectedIndices = [];
            rows.forEach(row => {{
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox && checkbox.checked) {{
                    selectedIndices.push(row.dataset.index);
                }}
            }});
            
            if (selectedIndices.length === 0) {{
                output.style.display = 'none';
                return;
            }}
            
            let code;
            if (selectedIndices.length === 1) {{
                code = `# Selected dataset:
dataset = nsai.datasets[${{selectedIndices[0]}}]`;
            }} else {{
                const indicesStr = selectedIndices.join(', ');
                code = `# Selected datasets:
datasets = [nsai.datasets[i] for i in [${{indicesStr}}]]`;
            }}
            
            // Copy to clipboard
            navigator.clipboard.writeText(code).then(() => {{
                // Update button text to show success
                const button = document.querySelector(`#${{containerId}} button[onclick="generateCode('${{containerId}}')"]`);
                const originalText = button.textContent;
                button.textContent = '✅ Copied!';
                button.style.backgroundColor = '#28a745';
                
                // Reset button after 2 seconds
                setTimeout(() => {{
                    button.textContent = originalText;
                    button.style.backgroundColor = '#007bff';
                }}, 2000);
            }}).catch(err => {{
                console.warn('Could not copy to clipboard:', err);
                // Fallback: still show the code for manual copying
            }});
            
            output.textContent = code;
            output.style.display = 'block';
        }}
        </script>
        """

        return html

    def __str__(self):
        """Display datasets as a nice table"""
        if not self._datasets:
            return "No datasets available"

        table_data = []
        for i, dataset in enumerate(self._datasets):
            table_data.append([i, dataset.email, dataset.name, dataset.syft_url])

        headers = ["Index", "Email", "Dataset Name", "Syft URL"]
        return tabulate(table_data, headers=headers, tablefmt="grid")

    def __repr__(self):
        return self.__str__()


# Create global instance
datasets = DatasetCollection()

# Export classes and instance
__all__ = ["Dataset", "DatasetCollection", "datasets"]
