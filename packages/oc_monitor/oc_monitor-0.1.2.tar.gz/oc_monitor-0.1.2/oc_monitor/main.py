import argparse
import os
from datetime import datetime
from data_monitor import MetaMonitor, IndexMonitor
from html_vis import ReportVisualiser

def _get_output_filepath(base_folder, base_filename, extension):
    """
    Generates a unique output filepath based on the current date.
    If a file with the same name exists, appends an incrementing number.
    """
    # Create the base file name with the current date (YYYYMMDD)
    date_str = datetime.now().strftime('%Y%m%d')
    file_name = f"{base_filename}_{date_str}"
    
    # Create the full path and check if it exists
    full_path = os.path.join(base_folder, f"{file_name}.{extension}")
    counter = 1

    # Increment the counter and check for existing files
    while os.path.exists(full_path):
        full_path = os.path.join(base_folder, f"{file_name}_{counter}.{extension}")
        counter += 1
    
    return full_path


def _prepare_output_folder(report_type, output_base_path):
    """
    Prepares the output folder structure for either MetaMonitor or IndexMonitor reports.
    Creates folders: <output_base_path>/meta_reports/YYYYMMDD/ or <output_base_path>/index_reports/YYYYMMDD/
    """
    date_str = datetime.now().strftime('%Y%m%d')
    base_folder = os.path.join(output_base_path, report_type, date_str)

    # Ensure the output directory exists
    os.makedirs(base_folder, exist_ok=True)
    
    return base_folder


def main():

    # os.chdir(os.path.join(os.getcwd(), 'monitor'))  # !!! SETS './monitor/' AS WORKING DIRECTORY !!!

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run MetaMonitor and/or IndexMonitor reports.")

    # Add arguments for MetaMonitor and IndexMonitor config file paths
    parser.add_argument(
        '--meta_config',
        default='meta_monitor_config.json',
        help='Filepath for MetaMonitor configuration (default: meta_monitor_config.json)'
    )
    
    parser.add_argument(
        '--index_config',
        default='index_monitor_config.json',
        help='Filepath for IndexMonitor configuration (default: index_monitor_config.json)'
    )
    
    # Add argument to specify which monitor to run: 'meta', 'index', or 'both'
    parser.add_argument(
        '--run',
        choices=['meta', 'index', 'both'],
        default='both',
        help='Specify which monitor to run: "meta", "index", or "both" (default: both)'
    )

    # Add argument for the base output path (default: 'results')
    parser.add_argument(
        '--output_base_path',
        default='../monitor_results',
        help='Base folder for reports output (default: ../monitor_results)'
    )

    args = parser.parse_args()

    template_fp = 'template.html'  # Same for Meta and Index monitor reports

    # Run MetaMonitor if specified
    if args.run in ['meta', 'both']:
        print("Running MetaMonitor...")

        # Prepare output folder structure for MetaMonitor
        meta_output_folder = _prepare_output_folder('meta_reports', args.output_base_path)

        # Create unique output filepaths for JSON and HTML
        meta_json_fp = _get_output_filepath(meta_output_folder, 'output_meta_monitor', 'json')
        meta_html_fp = _get_output_filepath(meta_output_folder, 'meta_monitor_vis', 'html')

        # Run MetaMonitor
        mm = MetaMonitor(args.meta_config, meta_json_fp)
        mm.run_tests()

        # Visualize the report
        mmv = ReportVisualiser(meta_json_fp, template_fp, meta_html_fp)
        mmv.generate_html()

        print(f"MetaMonitor JSON report generated: {meta_json_fp}")
        print(f"MetaMonitor HTML report generated: {meta_html_fp}")

    # Run IndexMonitor if specified
    if args.run in ['index', 'both']:
        print("Running IndexMonitor...")

        # Prepare output folder structure for IndexMonitor
        index_output_folder = _prepare_output_folder('index_reports', args.output_base_path)

        # Create unique output filepaths for JSON and HTML
        index_json_fp = _get_output_filepath(index_output_folder, 'output_index_monitor', 'json')
        index_html_fp = _get_output_filepath(index_output_folder, 'index_monitor_vis', 'html')

        # Run IndexMonitor
        im = IndexMonitor(args.index_config, index_json_fp)
        im.run_tests()

        # Visualize the report
        imv = ReportVisualiser(index_json_fp, template_fp, index_html_fp)
        imv.generate_html()

        print(f"IndexMonitor JSON report generated: {index_json_fp}")
        print(f"IndexMonitor HTML report generated: {index_html_fp}")

if __name__ == '__main__':
    main()
