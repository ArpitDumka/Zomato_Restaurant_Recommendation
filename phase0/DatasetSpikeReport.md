# Dataset spike report (Phase 0)

Generated: `2026-05-01T05:37:59.024207+00:00` (UTC)

## Source

- **Dataset:** `ManikaSaini/zomato-restaurant-recommendation`
- **Split:** `train`
- **Rows sampled for stats:** 8000 (streaming cap `8000`)

## Column keys (authoritative for field mapping)

[
  "url",
  "address",
  "name",
  "online_order",
  "book_table",
  "rate",
  "votes",
  "phone",
  "location",
  "rest_type",
  "dish_liked",
  "cuisines",
  "approx_cost(for two people)",
  "reviews_list",
  "menu_item",
  "listed_in(type)",
  "listed_in(city)"
]

## Null / empty counts (in sample)

Column | Empty or null count | Share
---|---:|---:
| `url` | 0 | 0.0% |
| `address` | 0 | 0.0% |
| `name` | 0 | 0.0% |
| `online_order` | 0 | 0.0% |
| `book_table` | 0 | 0.0% |
| `rate` | 1106 | 13.8% |
| `votes` | 0 | 0.0% |
| `phone` | 154 | 1.9% |
| `location` | 1 | 0.0% |
| `rest_type` | 35 | 0.4% |
| `dish_liked` | 4440 | 55.5% |
| `cuisines` | 9 | 0.1% |
| `approx_cost(for two people)` | 14 | 0.2% |
| `reviews_list` | 0 | 0.0% |
| `menu_item` | 0 | 0.0% |
| `listed_in(type)` | 0 | 0.0% |
| `listed_in(city)` | 0 | 0.0% |

## Example row (first observed)

```json
{
  "url": "https://www.zomato.com/bangalore/jalsa-banashankari?context=eyJzZSI6eyJlIjpbNTg2OTQsIjE4Mzc1NDc0IiwiNTkwOTAiLCIxODM4Mjk0NCIsIjE4MjI0Njc2IiwiNTkyODkiLCIxODM3MzM4NiJdLCJ0IjoiUmVzdGF1cmFudHMgaW4gQmFuYXNoYW5rYXJpIHNlcnZpbmcgQnVmZmV0In19",
  "address": "942, 21st Main Road, 2nd Stage, Banashankari, Bangalore",
  "name": "Jalsa",
  "online_order": "Yes",
  "book_table": "Yes",
  "rate": "4.1/5",
  "votes": 775,
  "phone": "080 42297555\r\n+91 9743772233",
  "location": "Banashankari",
  "rest_type": "Casual Dining",
  "dish_liked": "Pasta, Lunch Buffet, Masala Papad, Paneer Lajawab, Tomato Shorba, Dum Biryani, Sweet Corn Soup",
  "cuisines": "North Indian, Mughlai, Chinese",
  "approx_cost(for two people)": "800",
  "reviews_list": "[('Rated 4.0', 'RATED\\n  A beautiful place to dine in.The interiors take you back to the Mughal era. The lightings are just perfect.We went there on the occasion of Christmas and so they had only limited items available. But the taste and service was not compromised at all.The only complaint is that the breads could have been better.Would surely like to come here again.'), ('Rated 4.0', 'RATED\\n  I was here for dinner with my family on a weekday. The restaurant was completely empty. Ambience is good with some good old hindi music. Seating arrangement are good too. We ordered masala papad, panner and baby corn starters, lemon and corrionder soup, butter roti, olive and chilli paratha. Food was fresh and good, service is good too. Good for family hangout.\\nCheers'), ('Rated 2.0', 'RATED\\n  Its a restaurant near to Banashankari BDA. Me along with few of my office friends visited to have buffet but unfortunately they only provide veg buffet. On inquiring they said this place is mostly visited by vegetarians. Anyways we ordered ala carte items which took ages to come. Food was ok ok. Definitely not visiting anymore.'), ('Rated 4.0', 'RATED\\n  We went here on a weekend and one of us had the buffet while two of us took Ala Carte. Firstly the ambience and service of this place is great! The buffet had a lot of items and the good was good. We had a Pumpkin Halwa intm the dessert which was amazing. Must try! The kulchas are great here. Cheers!'), ('Rated 5.0', 'RATED\\n  The best thing about the place is it\u00c3\u0083\\x83\u00c3\u0082\\x83\u00c3\u0083\\x82\u00c3\u0082\\x82\u00c3\u0083\\x83\u00c3\u0082\\x82\u00c3\u0083\\x82\u00c3\u0082\\x92s ambiance. Second best thing was yummy ? food. We try buffet and buffet food was not disappointed us.\\nTest ?. ?? ?? ?? ?? ??\\nQuality ?. ??????????.\\nService: Staff was very professional and friendly.\\n\\nOverall experience was excellent.\\n\\nsubirmajumder85.wixsite.com'), ('Rated 5.0', 'RATED\\n  Great food and pleasant ambience. Expensive but Coll place to chill and relax......\\n\\nService is really very very good and friendly staff...\\n\\nFood : 5/5\\nService : 5/5\\nAmbience :5/5\\nOverall :5/5'), ('Rated 4.0', 'RATED\\n  Good ambience with tasty food.\\nCheese chilli paratha with Bhutta palak methi curry is a good combo.\\nLemon Chicken in the starters is a must try item.\\nEgg fried rice was also quite tasty.\\nIn the mocktails, recommend \"Alice in Junoon\". Do not miss it.'), ('Rated 4.0', 'RATED\\n  You can\u00c3\u0083\\x83\u00c3\u0082\\x83\u00c3\u0083\\x82\u00c3\u0082\\x82\u00c3\u0083\\x83\u00c3\u0082\\x82\u00c3\u0083\\x82\u00c3\u0082\\x92t go wrong with Jalsa. Never been a fan of their buffet and thus always order alacarte\u00c3\u0083\\x83\u00c3\u0082\\x83\u00c3\u0083\\x82\u00c3\u0082\\x82\u00c3\u0083\\x83\u00c3\u0082\\x82\u00c3\u0083\\x82\u00c3\u0082\\x92. Service at times can be on the slower side but food is worth the wait.'), ('Rated 5.0', 'RATED\\n  Overdelighted by the service and food provided at this place. A royal and ethnic atmosphere builds a strong essence of being in India and also the quality and taste of food is truly authentic. I would totally recommend to visit this place once.'), ('Rated 4.0', 'RATED\\n  The place is nice and comfortable. Food wise all jalea outlets maintain a good standard. The soya chaap was a standout dish. Clearly one of trademark dish as per me and a must try.\\n\\nThe only concern is the parking. It very congested and limited to just 5cars. The basement parking is very steep and makes it cumbersome'), ('Rated 4.0', 'RATED\\n  The place is nice and comfortable. Food wise all jalea outlets maintain a good standard. The soya chaap was a standout dish. Clearly one of trademark dish as per me and a must try.\\n\\nThe only concern is the parking. It very congested and limited to just 5cars. The basement parking is very steep and makes it cumbersome'), ('Rated 4.0', 'RATED\\n  The place is nice and comfortable. Food wise all jalea outlets maintain a good standard. The soya chaap was a standout dish. Clearly one of trademark dish as per me and a must try.\\n\\nThe only concern is the parking. It very congested and limited to just 5cars. The basement parking is very steep and makes it cumbersome')]",
  "menu_item": "[]",
  "listed_in(type)": "Buffet",
  "listed_in(city)": "Banashankari"
}
```

## `rate` — sample raw values (top frequencies in sample)

| Value | Count |
|---|---:|
| 3.8/5 | 611 |
| 3.9/5 | 604 |
| 3.7/5 | 595 |
| 3.6/5 | 575 |
| 4.0/5 | 461 |
| NEW | 427 |
| 3.5/5 | 423 |
| 4.1/5 | 419 |
| 3.4/5 | 353 |
| 3.3/5 | 335 |
| 3.2/5 | 316 |
| 4.2/5 | 290 |

## `approx_cost(for two people)` — sample raw values (top frequencies)

| Value | Count |
|---|---:|
| 300 | 1143 |
| 400 | 1040 |
| 500 | 751 |
| 200 | 746 |
| 600 | 547 |
| 250 | 476 |
| 800 | 412 |
| 150 | 384 |
| 700 | 282 |
| 350 | 265 |
| 1,000 | 236 |
| 450 | 223 |

## `listed_in(city)` — top values in sample

| City | Count |
|---|---:|
| Brigade Road | 1769 |
| Bannerghatta Road | 1617 |
| Basavanagudi | 1266 |
| Brookefield | 1258 |
| Bellandur | 1227 |
| Banashankari | 863 |

## `cuisines` — random variety (first 12 distinct in walk order)

- North Indian, Mughlai, Chinese
- Chinese, North Indian, Thai
- Cafe, Mexican, Italian
- South Indian, North Indian
- North Indian, Rajasthani
- North Indian
- North Indian, South Indian, Andhra, Chinese
- Pizza, Cafe, Italian
- Cafe, Italian, Continental
- Cafe, Mexican, Italian, Momos, Beverages
- Cafe
- Cafe, Chinese, Continental, Italian

> Re-run `python phase0/dataset_spike.py` after pinning a dataset revision if you need a frozen snapshot.
