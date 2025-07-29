import argparse
import asyncio
import logging
import sys

from loguru import logger

from xxy.__about__ import __version__
from xxy.agent import build_table
from xxy.config import load_config
from xxy.data_source.folder import FolderDataSource
from xxy.result_writer.csv import CsvResultWriter
from xxy.rongda_agent import (
    process_document_question,
    process_document_question_with_doc_id,
)


def config_log_level(v: int) -> None:
    logger.remove()
    log_format = "<level>{message}</level>"
    if v >= 4:
        logger.add(sys.stderr, level="TRACE", format=log_format)
    elif v >= 3:
        logger.add(sys.stderr, level="DEBUG", format=log_format)
    elif v >= 2:
        logger.add(sys.stderr, level="INFO", format=log_format)
    elif v >= 1:
        logger.add(sys.stderr, level="SUCCESS", format=log_format)
    else:
        logger.add(sys.stderr, level="WARNING", format=log_format)

    if v < 4:
        # avoid "WARNING! deployment_id is not default parameter."
        langchain_logger = logging.getLogger("langchain.chat_models.openai")
        langchain_logger.disabled = True


async def command_query(args: argparse.Namespace) -> None:
    data_source = FolderDataSource(args.folder_path)
    with CsvResultWriter(args.o) as result_writer:
        await build_table(data_source, args.t, args.d, args.n, result_writer)


async def command_config(args: argparse.Namespace) -> None:
    load_config(gen_cfg=True)


async def command_rongda(args: argparse.Namespace) -> None:
    """Handle rongda subcommand"""
    try:
        logger.info("🚀 Starting Rongda Agent...")
        logger.info(f"❓ Question: {args.question}")

        if args.doc_id:
            # Direct document analysis
            logger.info(f"📄 Analyzing document: {args.doc_id}")
            result = await process_document_question_with_doc_id(
                args.doc_id, args.question
            )
        else:
            # Search and analyze
            company_codes = args.company_codes or []
            logger.info(f"🏢 Company codes: {company_codes}")
            result = await process_document_question(
                user_question=args.question,
                company_code=company_codes,
                doc_id=args.doc_id,
            )

        # Output the result
        print(result)

        logger.success("✅ Analysis completed successfully!")

    except KeyboardInterrupt:
        logger.warning("🛑 Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error during analysis: {str(e)}")
        sys.exit(1)


async def amain() -> None:
    parser = argparse.ArgumentParser(description="xxy-" + __version__)
    parser.add_argument("-v", action="count", default=0, help="verbose level.")
    parser.add_argument(
        "-c",
        default="",
        help="Configuration file path. if not provided, use `~/.xxy_cfg.json` .",
    )
    subparsers = parser.add_subparsers(required=True, help="sub-command help")

    # create the parser for the "foo" command
    parser_query = subparsers.add_parser("query", help="Query entity from documents.")
    parser_query.set_defaults(func=command_query)
    parser_query.add_argument(
        "folder_path",
        help="Folder path to search for documents.",
    )
    parser_query.add_argument(
        "-t",
        nargs="*",
        help="Target company",
    )
    parser_query.add_argument(
        "-d",
        nargs="+",
        required=True,
        help="Report date",
    )
    parser_query.add_argument(
        "-n",
        nargs="+",
        required=True,
        help="Entity name",
    )
    parser_query.add_argument(
        "-o",
        default="output.csv",
        help="Output file path",
    )
    parser_config = subparsers.add_parser(
        "config",
        help="Edit configuration file.",
    )
    parser_query.add_argument(
        "--gen",
        help="Regenerate config from environment variables.",
    )
    parser_config.set_defaults(func=command_config)

    # create the parser for the "rongda" command
    parser_rongda = subparsers.add_parser(
        "rongda",
        help="Query financial documents using Rongda agent.",
        description="Rongda Financial Document Analysis Agent",
        epilog="""
Examples:
  # Search and analyze documents
  python -m xxy rongda "分析2023年营业收入情况" --company "000001 平安银行"
  
  # Multiple company codes
  python -m xxy rongda "对比各公司盈利能力" --company "000001" --company "000002"
  
  # Analyze specific document
  python -m xxy rongda "分析这份报告的主要财务指标" --doc-id "report123.html"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_rongda.set_defaults(func=command_rongda)
    parser_rongda.add_argument(
        "question",
        help="Your question about the financial documents (in Chinese or English)",
    )
    parser_rongda.add_argument(
        "--company",
        "-c",
        action="append",
        dest="company_codes",
        help="Company code(s) to search in. Can be used multiple times for multiple companies.",
    )
    parser_rongda.add_argument(
        "--doc-id",
        "-d",
        dest="doc_id",
        help="Specific document ID to analyze (skips search phase)",
    )
    args = parser.parse_args()

    # Special validation for rongda command
    if (
        hasattr(args, "question")
        and hasattr(args, "company_codes")
        and hasattr(args, "doc_id")
    ):
        if not args.doc_id and not args.company_codes:
            parser.error("rongda: Either --company or --doc-id must be provided")

    config_log_level(args.v)
    await args.func(args)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
