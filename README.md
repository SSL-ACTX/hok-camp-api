<div align="center">
  <img src="https://wsrv.nl/?url=https://ik.imagekit.io/y4xxnrbcqagasdtawd67/DEV/hok_cp.png&q=70&w=512&output=webp&maxage=30d" alt="Honor of Kings API Glitched Logo" width="160"/>
  <h1>Honor of Kings Camp Unofficial API</h1>
  <p>An unofficial, asynchronous, and feature-rich Python wrapper for the Honor of Kings (HOK) Camp API.</p>
</div>

<div align="center">

[![PyPI Version](https://img.shields.io/pypi/v/hok-camp-api?style=for-the-badge&logo=pypi&color=blue)](https://pypi.org/project/hok-camp-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/hok-camp-api?style=for-the-badge&logo=python&color=blue)](https://pypi.org/project/hok-camp-api/)
[![License](https://img.shields.io/pypi/l/hok-camp-api?style=for-the-badge&color=green)](https://github.com/SSL-ACTX/hok-camp-api/blob/main/LICENSE)

</div>

---

## ⚠️ Disclaimer

This is an **unofficial** library and is not affiliated with, endorsed, created, or sponsored by Tencent Games or TiMi Studio Group. All trademarks, service marks, trade names, trade dress, product names, and logos appearing on the site are the property of their respective owners.

This library is a community-driven project intended for educational and research purposes. Data is provided "as is" without warranty of any kind. Please use this library responsibly and respect the terms of service of the Honor of Kings Camp website.

---

This library provides a powerful, typed, and asynchronous interface to fetch a wide variety of data from the Honor of Kings Camp website, including hero details, seasonal adjustments, ranking statistics, and player reviews.

It's designed for performance and security, featuring intelligent local caching, on-demand security token generation, and automatic hash verification for all downloaded components.

## ✨ Key Features

*   **Fully Asynchronous:** Built with `asyncio` and `httpx` for high-performance, non-blocking I/O.
*   **Intelligent Security Management:** Automatically downloads the required `camp-security` executable for your platform (Windows, macOS, Linux), manages it as a background daemon, and maintains a persistent pool of security tokens for maximum speed.
*   **Secure by Default:** All downloaded executables are cryptographically verified against known SHA-256 hashes to prevent tampering.
*   **Robust Caching:** Features a persistent SQLite database for API responses, powered by performance-tuned settings.
*   **Type-Hinted Models:** Uses Python `dataclasses` for all API responses, providing clear data structures and editor auto-completion.
*   **Performance Optimized:** Uses `orjson` for rapid JSON processing and optimized SQLite settings for high-throughput database operations.
*   **User-Friendly CLI:** Displays rich progress bars and concise, helpful status messages for background operations like downloads and cache warm-ups.
*   **Dual-Client Approach:**
    *   **`HOKAPI` (Low-Level):** A stable, direct 1-to-1 mapping of API endpoints for maximum control and reliability.
    *   **`HOKClient` (High-Level):** A convenience wrapper that automatically handles resource management and data enrichment (WIP).

## ⚙️ Installation

The library requires Python 3.8 or newer.

You can install it directly from PyPI along with its recommended dependencies:

```bash
pip install hok-camp-api
```
*   `rich` is used for beautiful command-line output.
*   `orjson` is a high-performance JSON library that significantly speeds up API response parsing.

## 🚀 Quick Start with `HOKAPI` (Recommended)

The `HOKAPI` client provides a stable, low-level interface that directly corresponds to the web API endpoints. This is the recommended client for most use cases as it offers the greatest control.

```python
import asyncio
from hok import HOKAPI, Position, RankType, cache_manager

async def main():
    # Initialize the cache database once for your application
    await cache_manager.initialize()

    # The HOKAPI client requires manual resource management
    api = HOKAPI(region=608, language="en")

    try:
        # 1. Fetch all heroes to create a name lookup table
        all_heroes = await api.get_all_heroes()
        hero_id_to_name = {hero.heroId: hero.heroName for hero in all_heroes}
        print(f"✅ Found {len(all_heroes)} heroes. First hero: {all_heroes[0].heroName}")

        # 2. Fetch raw hero rankings for Mid Lane
        mid_lane_tiers = await api.get_hero_rankings(
            rank_type=RankType.TIER,
            position=Position.MID_LANE
        )

        print("\n--- Top 3 Mid Lane Tiers ---")
        for i, rank_entry in enumerate(mid_lane_tiers[:3]):
            # 3. Manually combine the data for the desired output
            hero_name = hero_id_to_name.get(rank_entry.heroId, "Unknown Hero")
            print(f"#{i}: {hero_name} (Win Rate: {rank_entry.winRate}%)")

    finally:
        # Clean up all resources when done
        print("\nCleaning up resources...")
        await api.close()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
```

## 🧪 High-Level `HOKClient` (Work in Progress)

For convenience, a high-level `HOKClient` is available. It aims to simplify common tasks by automatically managing resources and enriching data from multiple endpoints.

**Note:** This client is still under development. While functional, its methods and return types may change in future versions. For production use, the low-level `HOKAPI` is recommended.

The `HOKClient` uses an `async with` statement for automatic resource management.

```python
import asyncio
from hok import HOKClient, Position, RankType

async def main():
    # HOKClient handles all setup and cleanup automatically
    async with HOKClient(region=608, language="en") as client:

        # 1. Get enriched hero rankings with just ONE method call
        mid_lane_tiers = await client.get_rich_hero_rankings(
            rank_type=RankType.TIER,
            position=Position.MID_LANE
        )

        print("--- Top 3 Mid Lane Tiers (via HOKClient) ---")
        for i, rich_entry in enumerate(mid_lane_tiers[:3]):
            # The client combines the data for you
            hero_name = rich_entry.hero_info.heroName
            win_rate = rich_entry.rank_data.winRate
            print(f"#{i}: {hero_name} (Win Rate: {win_rate}%)")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 API Reference

### `HOKAPI` (Low-Level Client)

All methods are `async` and return the raw data models.

| Method | Description |
| :--- | :--- |
| `api.get_all_heroes()` | Fetches brief information for all available heroes. |
| `api.get_hero_details(hero_id)` | Fetches comprehensive data for a specific hero. |
| `api.get_hero_rankings(rank_type, position)` | Gets hero rankings by tier, win rate, etc., for a specific lane. |
| `api.get_seasonal_adjustments()` | Retrieves hero balance changes for the current season. |
| `api.get_hero_reviews()` | Fetches community reviews for all heroes. |
| `api.get_information_cards()` | Gets categorized information cards (e.g., lore, guides). |
| `api.get_homepage_content(page)` | Fetches the main content feed from the Camp homepage. |
| `api.close()` | **Required.** Closes the network client and security daemon. |

### Architecture & Managers

For advanced control, you can directly interact with the library's singleton managers.

*   `cache_manager`: Manages the persistent SQLite cache. Call `await cache_manager.initialize()` once on application startup.
*   `security_manager`: Manages the `camp-security` daemon. The `HOKAPI.close()` method handles its shutdown.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
