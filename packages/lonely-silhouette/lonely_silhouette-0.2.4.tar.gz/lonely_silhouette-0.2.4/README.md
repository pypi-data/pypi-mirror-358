> いや待て、この孤独な𝑆𝑖𝑙ℎ𝑜𝑢𝑒𝑡𝑡𝑒は…？

## Installation

```console
pip install lonely-silhouette
```

## Usage

```python
from lonely_silhouette import lonely_silhouette

print(lonely_silhouette("いや待て、この孤独なシルエットは…？"))
# いや待て、この孤独な𝑠𝑖𝑙ℎ𝑜𝑢𝑒𝑡𝑡𝑒は…？

print(lonely_silhouette("飛んで火にいる夏の虫"))
# 飛んで火にいる夏の𝑖𝑛𝑠𝑒𝑐𝑡

print(lonely_silhouette("祇園精舎の鐘の声"))
# 祇園精舍の鐘の𝑣𝑜𝑖𝑐𝑒
print(lonely_silhouette("諸行無常の響きあり"))
# 諸行無常の𝑒𝑐ℎ𝑜あり
```

### Using programmatically

```python
from lonely_silhouette import lonely_silhouette, FontStyle

print(lonely_silhouette("いや待て、この孤独なシルエットは…？"))
# いや待て、この孤独な𝑠𝑖𝑙ℎ𝑜𝑢𝑒𝑡𝑡𝑒は…？

print(lonely_silhouette("いや待て、この孤独なシルエットは…？", font_style=FontStyle.SCRIPT))
# いや待て、この孤独な𝓈𝒾𝓁𝒽ℴ𝓊ℯ𝓉𝓉ℯは…？
```

### Using as CLI

```console
$ python -m lonely_silhouette "いや待て、この孤独なシルエットは…？"
いや待て、この孤独な𝑠𝑖𝑙ℎ𝑜𝑢𝑒𝑡𝑡𝑒は…？

$ python -m lonely_silhouette --font-style script "いや待て、この孤独なシルエットは…？"
いや待て、この孤独な𝓈𝒾𝓁𝒽ℴ𝓊ℯ𝓉𝓉ℯは…？
```

## LICENSE

![](https://mirrors.creativecommons.org/presskit/icons/cc.svg) ![](https://mirrors.creativecommons.org/presskit/icons/zero.svg)

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)

see LICENSE file

## Acknowledgement

This package uses the JMdict dictionary file that comes from [the JMdict/EDICT project](https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project) by [Electronic Dictionary Research and Development Group](https://www.edrdg.org/) (EDRDG). The dictionary file is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode) by them.
