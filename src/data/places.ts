export interface Stat {
  label: string;
  value: string;
}

export interface Section {
  heading: string;
  body: string[];
}

export interface Highlight {
  name: string;
  meta: string;
  text: string;
}

export interface Season {
  months: string;
  label: string;
  text: string;
}

export interface Festival {
  name: string;
  when: string;
  text: string;
}

export interface Place {
  id: string;
  title: string;
  subtitle: string;
  tagline: string;
  hero: string;
  heroCredit: string;
  /** CSS object-position for the hero crop, tuned per photograph. */
  heroFocus: string;
  /** CSS colour used to tint the whole destination page. */
  accent: string;
  accentDeep: string;
  lede: string;
  stats: Stat[];
  sections: Section[];
  highlights: Highlight[];
  experiences: Highlight[];
  seasons: Season[];
  festivals: Festival[];
  food: string[];
  practical: Stat[];
  mindful: string;
}

export const places: Place[] = [
  {
    id: "jaisalmer",
    title: "Jaisalmer",
    subtitle: "The Golden City",
    tagline: "A living fort of honey sandstone, marooned in the Thar Desert.",
    hero: "images/jaisalmer.jpg",
    heroFocus: "center 44%",
    heroCredit: "Jaisalmer Fort above Gadisar Lake at golden hour",
    accent: "#e8a33d",
    accentDeep: "#8a4f1c",
    lede: "Jaisalmer is the last big town before the Thar Desert turns into nothing but sand and sky, and it looks the part: an entire city cut from yellow Jurassic sandstone that turns the colour of melted honey an hour before sunset. Its fort is not a monument you visit and leave — roughly a quarter of the old city still lives inside the walls, which makes Sonar Quila one of the very few genuinely inhabited forts left anywhere in the world.",
    stats: [
      { label: "Founded", value: "1156 CE" },
      { label: "Founder", value: "Rawal Jaisal, Bhati Rajput" },
      { label: "Status", value: "UNESCO World Heritage" },
      { label: "Fort bastions", value: "99" },
      { label: "Elevation", value: "~250 m" },
      { label: "Best season", value: "October – March" },
    ],
    sections: [
      {
        heading: "Why a city here, of all places",
        body: [
          "Rawal Jaisal, a Bhati Rajput chief, abandoned the old capital at Lodurva in 1156 CE and moved his people onto Trikuta Hill — a triple-peaked ridge that rose out of flat desert and could be defended from every side. The move was strategic rather than romantic: Jaisalmer sat directly on the caravan route linking India to Persia, Arabia, Egypt and Central Asia, and for six centuries the town taxed every string of camels that passed.",
          "That toll money is the reason a remote desert outpost is filled with some of the most obsessively carved stone in India. Merchant families competed to out-build one another, and their havelis — private mansions with screens cut so fine they read as lace — still line the lanes below the fort.",
          "The caravan economy collapsed twice: first when the British opened the port of Bombay and sea freight undercut the desert route, then decisively at Partition in 1947, when the border with Pakistan closed the western roads for good. Jaisalmer went quiet for a generation. It was tourism, and the Indian Army's presence near the border, that brought it back.",
        ],
      },
      {
        heading: "The fort that people still live in",
        body: [
          "Sonar Quila — the Golden Fort — runs about 460 metres long and 230 metres wide, ringed by 99 bastions and a triple wall that steps up the hill in tiers. You enter through four successive gateways: Akhai Pol, Suraj Pol, Ganesh Pol and Hawa Pol, each angled so an attacking elephant could never build up a straight charge.",
          "Inside, the streets are barely wide enough for a motorbike. There are homes, guesthouses, a post office, tailors, cows, and children walking to school, all inside 12th-century military architecture. The Raj Mahal palace stands over the main square, Dussehra Chowk, where the maharawals once held court.",
          "The fort's seven Jain temples, built between the 12th and 15th centuries, are the artistic peak of the place — Chandraprabhu, Rikhabdev, Parshvanath, Shantinath, Kunthunath, Sambhavnath and Shitalnath, connected by corridors and carved in the same lacework style as Mount Abu's Dilwara temples. Tucked beneath them is the Gyan Bhandar, a library holding palm-leaf manuscripts that predate the fort itself.",
          "The stone was quarried nearby and contains no mortar in the older sections: blocks are cut to interlock and held by their own weight, which is why the fort flexes rather than cracks.",
        ],
      },
      {
        heading: "Sandstone as a competitive sport",
        body: [
          "Patwon Ki Haveli is really five mansions built side by side between 1805 and 1860 by Guman Chand Patwa, a trader in gold and silver brocade who reportedly also dealt in opium. Each son got a house, and each house got a more elaborate facade than the last. The first is now a museum, and the rooftop gives the best close view of the fort.",
          "Salim Singh Ki Haveli is the strange one: a prime minister's house whose upper storey flares outward into 38 balconies shaped, depending on who is describing it, like a peacock's tail or a ship's stern. Local legend says Salim Singh started building two extra floors so it would overtop the maharawal's palace, and the ruler had them torn down.",
          "Nathmal Ki Haveli was carved in the 1880s by two brothers who worked on opposite sides of the building at the same time and never compared notes. The two halves are almost — but very visibly not — identical, which is the whole charm of it.",
        ],
      },
      {
        heading: "Water in a place with none",
        body: [
          "Gadisar Lake was dug in 1367 by Maharawal Gadsi Singh as the town's entire water supply — a rainwater harvesting tank in a region that gets under 200 mm a year. It is ringed by ghats, small shrines and chhatris, and entered through the Tilon-ki-Pol, an ornate sandstone archway reputedly paid for by a courtesan and nearly demolished by the offended royal court.",
          "In winter the lake fills with migratory birds and the light at dawn is extraordinary. It is also the cleanest illustration of the problem facing Jaisalmer today: the fort was engineered for a town that used a few litres of water per person per day. Modern piped supply and tourism have saturated the hill's ancient drainage, undermining foundations that were never meant to get wet. The World Monuments Fund has repeatedly listed the fort as endangered, and several bastions have partially collapsed since the 1990s.",
        ],
      },
    ],
    highlights: [
      {
        name: "Jaisalmer Fort",
        meta: "12th century · UNESCO",
        text: "The reason to come. Walk the ramparts at sunrise before the day-trippers arrive, then again after dark when the lanes empty and the sandstone holds the day's heat.",
      },
      {
        name: "Patwon Ki Haveli",
        meta: "1805–1860 · five mansions",
        text: "The most ornate private architecture in the desert. Pay for the museum floor; the rooftop view alone justifies it.",
      },
      {
        name: "Gadisar Lake",
        meta: "1367 · rainwater reservoir",
        text: "Chhatris, ghats and pelicans. Take a pedal boat out at first light and photograph the fort reflected behind you.",
      },
      {
        name: "Bada Bagh",
        meta: "16th–20th century · royal cenotaphs",
        text: "A hillside of sandstone chhatris marking the cremation sites of Jaisalmer's rulers, with wind turbines turning behind them. The single best sunset in the district.",
      },
      {
        name: "Kuldhara",
        meta: "Abandoned c. 1825",
        text: "An entire Paliwal Brahmin village emptied overnight, supposedly under a curse laid on the minister who coveted the headman's daughter. The ruins are eerie and the story is better told there than here.",
      },
      {
        name: "Sam & Khuri Dunes",
        meta: "42 km / 45 km west",
        text: "Sam is the big, busy dune field with camel trains and evening folk performances. Khuri is smaller, quieter and better if you want the desert to actually feel like a desert.",
      },
      {
        name: "Desert National Park",
        meta: "3,162 km² · Great Indian Bustard",
        text: "One of the last strongholds of the critically endangered Great Indian Bustard, plus chinkara, desert fox and raptors over an ocean of scrub and shifting sand.",
      },
      {
        name: "Jain temples & Gyan Bhandar",
        meta: "12th–15th century",
        text: "Seven interconnected temples of extraordinarily fine carving, and a library of palm-leaf manuscripts beneath them. Open to visitors only in the morning.",
      },
    ],
    experiences: [
      {
        name: "Sleep in the dunes",
        meta: "Overnight",
        text: "Camel out to a dune camp in the late afternoon, eat under the stars and wake before dawn. Choose a camp away from the Sam strip if you want silence rather than a loudspeaker.",
      },
      {
        name: "Walk the fort at 6 a.m.",
        meta: "90 minutes",
        text: "The fort belongs to its residents before about nine in the morning. This is when you see it as a town rather than an attraction.",
      },
      {
        name: "Listen to Manganiyar musicians",
        meta: "Evenings",
        text: "The Manganiyar and Langa communities are hereditary desert musicians whose repertoire goes back centuries. Seek out a small courtyard performance rather than a hotel buffet set.",
      },
      {
        name: "Buy from the source",
        meta: "Half a day",
        text: "Jaisalmer is known for patchwork appliqué, mirrorwork, camel-leather goods and hand-woven wool. Prices in the fort lanes are tourist prices; the town bazaar below is where locals shop.",
      },
    ],
    seasons: [
      {
        months: "Oct – Feb",
        label: "Prime",
        text: "Days around 22–28 °C, nights cold enough for a jacket and genuinely freezing in the dunes in late December. This is when to come.",
      },
      {
        months: "Mar – Apr",
        label: "Warm but workable",
        text: "Climbing past 35 °C by mid-March. Mornings and evenings are still lovely; midday is not.",
      },
      {
        months: "May – Jun",
        label: "Avoid",
        text: "Regularly 45 °C and above, with sandstorms. Even the desert camps shut down.",
      },
      {
        months: "Jul – Sep",
        label: "Off-season",
        text: "A little rain, dramatic skies, far fewer people and low prices. Hot and humid, but the desert briefly greens.",
      },
    ],
    festivals: [
      {
        name: "Desert Festival (Maru Mahotsav)",
        when: "February, around Magh Purnima",
        text: "Three days of camel races, turban-tying contests, folk dance, and the famously absurd Mr Desert competition, ending with a concert on the Sam dunes.",
      },
      {
        name: "Gangaur",
        when: "March – April",
        text: "Processions of decorated Gauri idols through the old town, celebrated across Rajasthan but intimate here.",
      },
      {
        name: "Jaisalmer Folk Music Festival",
        when: "Winter, dates vary",
        text: "Manganiyar and Langa performers alongside touring artists, staged against the fort walls.",
      },
    ],
    food: [
      "Ker sangri — desert berries and beans, slow-cooked in yoghurt and spice",
      "Gatte ki sabzi — gram-flour dumplings in a tangy yoghurt curry",
      "Makhaniya lassi — thick, saffron-and-cardamom lassi",
      "Pyaaz kachori — flaky onion-stuffed pastry, eaten hot at breakfast",
      "Dal baati churma — the Rajasthani staple, baked wheat balls drowned in ghee",
      "Murgh-e-Subz & laal maas — for the meat-eating half of the Rajput kitchen",
    ],
    practical: [
      { label: "Nearest airport", value: "Jaisalmer (JSA), seasonal · Jodhpur (JDH), 285 km" },
      { label: "By rail", value: "Jaisalmer station — Jodhpur 5–6 h, Delhi ~18 h overnight" },
      { label: "By road", value: "Jodhpur 285 km (5 h) · Bikaner 330 km · Udaipur 490 km" },
      { label: "Getting around", value: "The fort is walk-only. Autos and hired jeeps for the dunes." },
      { label: "Typical stay", value: "2–3 nights, including one in the desert" },
      { label: "Languages", value: "Marwari, Hindi; English widely spoken in tourism" },
    ],
    mindful:
      "The fort is a fragile, inhabited heritage site with a serious drainage problem. Stay in the town below rather than inside the walls if you can, keep water use down, and don't buy wildlife products or antique stone fragments offered in the lanes.",
  },
  {
    id: "jaipur",
    title: "Jaipur",
    subtitle: "The Pink City",
    tagline: "India's first planned city, painted rose and laid out by the stars.",
    hero: "images/jaipur.jpg",
    heroFocus: "center 40%",
    heroCredit: "Hawa Mahal lit at dusk, its five storeys of jharokhas stepping back to a crown",
    accent: "#e2573f",
    accentDeep: "#7d2418",
    lede: "Jaipur was not allowed to grow the way other Indian cities did. It was drawn on paper first — a nine-block grid derived from the Vastu Shastra, with streets of fixed width and shopfronts of fixed height — and then built, in 1727, by a maharaja who was also a serious astronomer. Nearly three centuries later the plan still holds, which is why the walled city reads as one enormous coherent object rather than a collection of buildings.",
    stats: [
      { label: "Founded", value: "18 November 1727" },
      { label: "Founder", value: "Maharaja Sawai Jai Singh II" },
      { label: "Chief architect", value: "Vidyadhar Bhattacharya" },
      { label: "Status", value: "UNESCO World Heritage, 2019" },
      { label: "Painted pink", value: "1876" },
      { label: "Best season", value: "October – March" },
    ],
    sections: [
      {
        heading: "A city designed before it was built",
        body: [
          "By the 1720s the Kachhwaha capital at Amber was out of water and out of room. Sawai Jai Singh II — a ruler who corresponded with European astronomers and had already built observatories in Delhi and Ujjain — decided to start again on the plain below, and to do it properly.",
          "His engineer, the Bengali scholar Vidyadhar Bhattacharya, laid the city out as a grid of nine rectangular sectors, mirroring the nine divisions of the Hindu cosmos in the Prastara plan of the Shilpa Shastra. One sector was displaced to accommodate a hill, and the missing block was added on the opposite side — a compromise you can still trace on a map today.",
          "The main bazaars run 111 feet wide, cross at right angles, and are lined with uniform colonnaded shopfronts with the residential quarters behind. The whole thing was walled, with seven gates, and completed in about four years. It was the first planned city in India and remains the only one of its era still functioning as designed.",
          "The pink came later. In 1876 Maharaja Sawai Ram Singh II had the walled city washed in terracotta to welcome Albert Edward, Prince of Wales — pink being the traditional colour of hospitality. It stuck, and a municipal bylaw has required it ever since.",
        ],
      },
      {
        heading: "Hawa Mahal, explained properly",
        body: [
          "Almost everyone photographs Hawa Mahal from the street and almost no one goes in, which is a mistake, because the building is not a palace at all. It is a screen — a five-storey extension added in 1799 to the back wall of the City Palace zenana so that royal women, who observed strict purdah, could watch street processions without being seen.",
          "Lal Chand Ustad designed it for Maharaja Sawai Pratap Singh in the shape of Krishna's crown, and gave it 953 small jharokha windows. Those windows are the working part: desert air forced through hundreds of small apertures accelerates and cools by the Venturi effect, which is where the name — Palace of Winds — comes from.",
          "It is barely a room deep. There are no staircases to speak of, just ramps, and the upper storeys are so thin the whole thing leans at about 87 degrees. Go in from the rear courtyard, climb to the top, and look out through the screens the way they were meant to be looked through.",
        ],
      },
      {
        heading: "Jai Singh's stone instruments",
        body: [
          "Jantar Mantar, finished in 1734, is not a decorative folly. It is a working observatory of nineteen masonry instruments, built at architectural scale precisely because bigger instruments give finer readings than brass ones.",
          "The Vrihat Samrat Yantra is a sundial 27 metres high whose shadow moves visibly — about a millimetre a second — and which reads local time to an accuracy of two seconds. The Jai Prakash Yantra is a pair of sunken hemispherical bowls you can walk inside, mapping the sky onto the ground. Twelve Rashivalaya instruments, one for each zodiac sign, are each aligned to a different ecliptic position.",
          "UNESCO inscribed the site in 2010 as the most significant, comprehensive and best-preserved historic observatory in India. It is also the one monument in Jaipur genuinely worth hiring a guide for; without explanation it looks like abstract sculpture.",
        ],
      },
      {
        heading: "Amber, and the forts above the city",
        body: [
          "Amber (pronounced Amer) was the Kachhwaha capital before Jaipur existed, and the fort that Raja Man Singh I began in 1592 is the more spectacular of the two sites. It climbs a ridge above Maota Lake in sandstone and marble, through the painted Ganesh Pol gateway into a sequence of courtyards.",
          "The Sheesh Mahal, the mirror palace, is lined with thousands of convex glass tiles imported from Belgium; a single candle in it is said to have lit the whole chamber. Opposite, the Sukh Niwas was air-conditioned in the 16th century by water piped down channels cut into the marble floor.",
          "Above Amber sits Jaigarh, the arsenal, which holds Jaivana — cast in 1720 and still the largest wheeled cannon on earth. It was test-fired once. Nahargarh, on the ridge directly over Jaipur, was the retreat, and gives the view that explains the whole city grid in one glance.",
        ],
      },
      {
        heading: "The bazaars are the point",
        body: [
          "Jaipur is one of the great craft cities of Asia and the trades are still geographically sorted, sector by sector, exactly as Jai Singh's plan intended. Johari Bazaar is gemstones and jewellery — Jaipur remains the world's largest centre for emerald cutting. Bapu Bazaar sells textiles and mojari slippers. Tripolia Bazaar is lac bangles. Maniharon ka Rasta is where the bangle-makers actually work.",
          "Outside the walls, Sanganer and Bagru are the block-printing villages: Sanganer for fine floral prints on white, Bagru for earthy dabu mud-resist work. Blue pottery — quartz rather than clay, glazed cobalt — is a Jaipur speciality that arrived via Persia and Central Asia and survives largely because of a deliberate revival in the 1960s.",
        ],
      },
    ],
    highlights: [
      {
        name: "Hawa Mahal",
        meta: "1799 · 953 windows",
        text: "Photograph it from the street at sunrise when the east light hits the facade, then go inside from the rear courtyard. Most visitors skip the interior and shouldn't.",
      },
      {
        name: "Amber Fort",
        meta: "From 1592 · UNESCO",
        text: "Allow three hours. Walk up rather than taking an elephant — the ride is contested on welfare grounds and the climb is short.",
      },
      {
        name: "Jantar Mantar",
        meta: "1734 · UNESCO",
        text: "Nineteen astronomical instruments including the world's largest stone sundial. Hire a guide; it is unintelligible without one.",
      },
      {
        name: "City Palace",
        meta: "1729 onward · still occupied",
        text: "Mubarak Mahal, Chandra Mahal, and Pritam Niwas Chowk with its four seasonal doorways — Peacock, Lotus, Green and Rose. The royal family still lives in the upper floors.",
      },
      {
        name: "Nahargarh Fort",
        meta: "1734 · ridge-top",
        text: "The sunset view over the entire grid. Stay for the lights coming on; the drive down is quick.",
      },
      {
        name: "Panna Meena ka Kund",
        meta: "16th century stepwell",
        text: "A symmetrical criss-cross stepwell near Amber, far quieter than the forts and startlingly photogenic.",
      },
      {
        name: "Albert Hall Museum",
        meta: "1887 · Indo-Saracenic",
        text: "Rajasthan's oldest museum, with an Egyptian mummy, Persian carpets and a superb collection of local metalwork. Floodlit and swarming with pigeons at night.",
      },
      {
        name: "Jal Mahal",
        meta: "Man Sagar Lake",
        text: "A five-storey palace with four floors underwater. You can't go in, but the lakeside view at dusk is a fixture of the drive to Amber.",
      },
    ],
    experiences: [
      {
        name: "Learn block printing",
        meta: "Half a day, Bagru or Sanganer",
        text: "Workshops in the printing villages will put a carved teak block in your hand and let you ruin a few metres of cloth. The best souvenir you can make.",
      },
      {
        name: "Eat at Masala Chowk",
        meta: "Evening",
        text: "An open-air food court in Ram Niwas Garden collecting Jaipur's legendary street vendors in one safe, walkable place — kachori, chaat, lassi, ghevar.",
      },
      {
        name: "Fly a kite in January",
        meta: "14 January",
        text: "On Makar Sankranti the entire city goes to the roof and the sky fills with paper. It is the single most joyful day in Jaipur's calendar.",
      },
      {
        name: "Walk the old city at dawn",
        meta: "2 hours",
        text: "Start at Chandpole and follow the grid east. Before the traffic starts you can actually see the architecture you came for.",
      },
    ],
    seasons: [
      {
        months: "Oct – Mar",
        label: "Prime",
        text: "Warm days, cool evenings, clear light. December and January nights drop near 8 °C — bring layers.",
      },
      {
        months: "Apr – Jun",
        label: "Hot",
        text: "40 °C plus and dry. Sightseeing collapses into early mornings and after five. Hotel rates are at their lowest.",
      },
      {
        months: "Jul – Sep",
        label: "Monsoon",
        text: "Intermittent heavy rain, green hills around Amber, dramatic skies, and Teej. Underrated if you don't mind getting wet.",
      },
    ],
    festivals: [
      {
        name: "Jaipur Literature Festival",
        when: "January",
        text: "Billed as the largest free literary festival in the world. Book accommodation months out.",
      },
      {
        name: "Makar Sankranti",
        when: "14 January",
        text: "The kite festival. Rooftops, loudspeakers, and a genuinely competitive sport of cutting rivals' strings.",
      },
      {
        name: "Gangaur",
        when: "March – April",
        text: "Eighteen days honouring Gauri, ending in a procession of palanquins from the City Palace — Jaipur's most important local festival.",
      },
      {
        name: "Teej",
        when: "August",
        text: "The monsoon festival, marked by green saris, swings hung in courtyards, and a royal elephant procession through the old city.",
      },
    ],
    food: [
      "Dal baati churma — the definitive Rajasthani plate",
      "Pyaaz kachori at Rawat — the city's most defended breakfast",
      "Laal maas — fiery mutton curry built on Mathania chillies",
      "Ghewar — a disc-shaped honeycomb sweet soaked in syrup, peak season at Teej",
      "Lassi at Lassiwala, Mirza Ismail Road — served in a clay kulhad, sold out by noon",
      "Mawa kachori & Rajasthani thali at Chokhi Dhani for the full theatrical version",
    ],
    practical: [
      { label: "Nearest airport", value: "Jaipur International (JAI), 13 km from centre" },
      { label: "By rail", value: "Delhi 4 h on Vande Bharat · Ahmedabad 9 h · Mumbai ~16 h" },
      { label: "By road", value: "Delhi 280 km (5 h, NH48) · Agra 240 km · Udaipur 395 km" },
      { label: "Getting around", value: "Metro on one line, plus autos, Uber/Ola. The walled city is best on foot." },
      { label: "Typical stay", value: "3 nights minimum; 4 if you're doing crafts" },
      { label: "Composite ticket", value: "One pass covers Amber, Nahargarh, Jantar Mantar, Albert Hall and more — good for two days" },
    ],
    mindful:
      "Elephant rides at Amber are a live animal-welfare issue; walking up or taking a jeep is the kinder option. Buy crafts from the workshops in Sanganer, Bagru and Maniharon ka Rasta where the makers are paid directly, rather than from emporium middlemen on the tourist circuit.",
  },
  {
    id: "udaipur",
    title: "Udaipur",
    subtitle: "The City of Lakes",
    tagline: "Marble palaces on still water, ringed by the oldest mountains in India.",
    hero: "images/udaipur.jpg",
    heroFocus: "center 50%",
    heroCredit: "Lake Pichola at sunset, with the Taj Lake Palace and City Palace",
    accent: "#3e9fb5",
    accentDeep: "#1b4f5e",
    lede: "Udaipur exists because Chittorgarh fell. When Akbar's armies took the old Mewar capital, Maharana Udai Singh II moved his court into a bowl in the Aravalli hills where a small lake already sat — and his successors spent the next four hundred years turning that lake into the most theatrical urban landscape in India. The Aravallis are among the oldest mountain ranges on earth, worn down to soft green ridges, and they hold the whole city in a kind of amphitheatre.",
    stats: [
      { label: "Founded", value: "1559 CE" },
      { label: "Founder", value: "Maharana Udai Singh II" },
      { label: "Dynasty", value: "Sisodia Rajputs of Mewar" },
      { label: "Lake Pichola", value: "Built 1362, 4 km × 3 km" },
      { label: "Elevation", value: "598 m" },
      { label: "Best season", value: "September – March" },
    ],
    sections: [
      {
        heading: "The capital that refused to surrender",
        body: [
          "Mewar's identity is built on not submitting. Where most Rajput houses eventually made terms with the Mughals — often sealed with a marriage — the Sisodias of Mewar held out, and paid for it. Chittorgarh was sacked three times. After the third siege in 1568, Udai Singh II founded a new capital deep in the hills, on ground far harder to reach with an army.",
          "His son Maharana Pratap fought Akbar's forces at Haldighati in 1576, lost the field, and then spent the rest of his life reclaiming Mewar territory from the forests rather than accepting a treaty. He is, four and a half centuries later, still the most venerated figure in Rajasthan.",
          "That history is why Udaipur's palaces feel different from Jaipur's. They are less Mughal-influenced, more inward-facing, built around courtyards and water rather than parade grounds.",
        ],
      },
      {
        heading: "A palace built by twenty-two men",
        body: [
          "The City Palace is the largest palace complex in Rajasthan, and it is not one building but eleven, accreted over roughly four hundred years by twenty-two successive Maharanas — each adding to the granite-and-marble mass on the eastern bank of Lake Pichola without demolishing what came before. The result is a single 244-metre facade concealing a warren of courtyards at a dozen different levels.",
          "Badi Mahal is a garden courtyard built on a natural rock outcrop, twenty-seven metres above the rest of the palace, with trees growing at roof height. Mor Chowk is inlaid with five peacocks — one for each of three seasons plus two — assembled from around five thousand pieces of coloured glass. Amar Vilas is the highest point, a hanging garden with fountains and lotus pools that borrows Mughal charbagh geometry.",
          "The Mewar family still occupies part of the complex; the rest is a museum and two hotels. The crystal gallery in Fateh Prakash holds a full crystal dinner service ordered from Birmingham in 1877 that arrived after the Maharana died and stayed in its crates, unopened, for 110 years.",
        ],
      },
      {
        heading: "The two island palaces",
        body: [
          "Jag Niwas, now the Taj Lake Palace, was built between 1743 and 1746 by Maharana Jagat Singh II as a summer retreat, and it covers its entire island — from the water it looks like white marble floating unsupported. It became a hotel in 1963 and a global shorthand for Indian luxury after appearing in Octopussy in 1983.",
          "Jag Mandir, the larger island to the south, is the historically interesting one. In 1623 Prince Khurram — later Emperor Shah Jahan — took refuge there during his revolt against his father Jahangir, and Mewar tradition holds that its domed pavilion and inlaid marble influenced what he later built at Agra. The ring of carved stone elephants guarding the jetty is original.",
          "Both are reached by boat from Rameshwar Ghat. Go in the last hour of daylight, when the hills go violet and the palace stone turns the colour of the sky.",
        ],
      },
      {
        heading: "Lakes, and what happens when they empty",
        body: [
          "Lake Pichola was dug in 1362 by a banjara grain trader named Pichhu, long before the city existed, and enlarged by Udai Singh II when he built his capital around it. Fateh Sagar to the north was created in 1678 and rebuilt in 1889 by Maharana Fateh Singh after a flood destroyed the earthen dam; the two are connected by a canal.",
          "The system is entirely rain-fed. In drought years — 2000, 2003 and 2016 among them — Pichola has dropped so far that people walked to the island palaces across cracked mud. The lakes are the city's economy as well as its scenery, and the current restoration work on the feeder catchments matters more than any monument.",
          "Saheliyon ki Bari, the Garden of the Maidens, is the best demonstration of what all that water made possible: an 18th-century pleasure garden whose fountains — lotus pools, an elephant fountain, a rain fountain that mimics monsoon showers — run entirely on gravity from the lake above, with no pumps at all.",
        ],
      },
      {
        heading: "Worth the drive",
        body: [
          "Kumbhalgarh, 85 km north, is ringed by a wall that runs for 36 kilometres — the second-longest continuous wall anywhere after the Great Wall of China, wide enough in places for eight horses abreast. It was never taken by direct assault, and Maharana Pratap was born inside it.",
          "Ranakpur, 90 km away, is a 15th-century Jain temple in white marble supported by 1,444 pillars, and no two of them are carved the same. The interior light in the late morning is something people travel for on its own.",
          "Closer in, Eklingji and Nagda at 22 km hold the temple of Mewar's patron deity, where the ruling Maharana traditionally worshipped as a regent on the god's behalf rather than as a king in his own right.",
        ],
      },
    ],
    highlights: [
      {
        name: "City Palace",
        meta: "1559 onward · 11 palaces",
        text: "Budget three hours. Enter through Badi Pol and work upward; the sequence of courtyards is designed to be walked in order.",
      },
      {
        name: "Lake Pichola boat ride",
        meta: "Golden hour",
        text: "The single best hour in Udaipur. Boats leave from Rameshwar Ghat inside the palace complex and stop at Jag Mandir.",
      },
      {
        name: "Jagdish Temple",
        meta: "1651 · Nagara style",
        text: "Thirty-two steps up to a brass Garuda and a black stone Vishnu. Active, loud at aarti, and right in the middle of the old town.",
      },
      {
        name: "Saheliyon ki Bari",
        meta: "Early 18th century",
        text: "Gravity-fed fountains, marble elephants and a lotus pool built for the queen's forty-eight attendants.",
      },
      {
        name: "Monsoon Palace (Sajjangarh)",
        meta: "1884 · hilltop",
        text: "Unfinished, semi-derelict, and positioned for the finest sunset in the region, looking out over the lakes and the Aravalli ridges.",
      },
      {
        name: "Bagore ki Haveli",
        meta: "18th century · Dharohar show",
        text: "A restored noble's mansion on Gangaur Ghat with a nightly hour of Mewari folk dance — including the astonishing bhavai, danced with nine pots balanced on the head.",
      },
      {
        name: "Kumbhalgarh Fort",
        meta: "85 km · UNESCO",
        text: "A 36-kilometre wall around a hilltop citadel, best seen from the ramparts at Badal Mahal. Pair it with Ranakpur in one long day.",
      },
      {
        name: "Ranakpur Jain Temple",
        meta: "90 km · 1,444 pillars",
        text: "Fifteenth-century marble of a fineness that is difficult to believe in person. Open to non-Jain visitors from around noon.",
      },
    ],
    experiences: [
      {
        name: "Learn miniature painting",
        meta: "2–3 hours",
        text: "The Mewar school of miniature is a living tradition here, worked with squirrel-hair brushes of a few bristles. Studios near Jagdish Temple teach short classes.",
      },
      {
        name: "Watch Dharohar at Bagore ki Haveli",
        meta: "Nightly, 7 p.m.",
        text: "An hour of Rajasthani folk dance in a lamplit courtyard. Arrive thirty minutes early — the good seats go fast and it is not ticketed in advance.",
      },
      {
        name: "Cycle or drive the Aravalli ridges",
        meta: "Half day",
        text: "The road out toward Eklingji and Nagda climbs through terraced fields and old step-wells, and shows you the Mewar that isn't lakes and palaces.",
      },
      {
        name: "Eat on a rooftop at dusk",
        meta: "Evening",
        text: "Half the old city is rooftop restaurants aimed squarely at the Lake Palace view. Choose one on the Ambrai or Hanuman Ghat side so you get the City Palace in frame instead.",
      },
    ],
    seasons: [
      {
        months: "Sep – Nov",
        label: "Best",
        text: "Lakes full from the monsoon, hills still green, temperatures in the mid-twenties. The most beautiful window of the year.",
      },
      {
        months: "Dec – Feb",
        label: "Cool and clear",
        text: "Crisp days, cold nights, peak tourist season and peak prices. Excellent light for photography.",
      },
      {
        months: "Mar – Jun",
        label: "Hot",
        text: "Rising to 40 °C in May. Lake levels drop. Mornings and evenings remain pleasant on the water.",
      },
      {
        months: "Jul – Aug",
        label: "Monsoon",
        text: "Heavy rain, waterfalls in the Aravallis, lakes refilling, and the city at its greenest. Hariyali Amavasya falls in this window.",
      },
    ],
    festivals: [
      {
        name: "Mewar Festival",
        when: "March – April, with Gangaur",
        text: "Processions of Gauri idols carried to Gangaur Ghat and taken out onto Lake Pichola in decorated boats, ending in fireworks.",
      },
      {
        name: "Hariyali Amavasya",
        when: "July – August",
        text: "A monsoon fair around Fateh Sagar marking the return of green to the hills, with a day reserved for women only.",
      },
      {
        name: "Shilpgram Utsav",
        when: "21–30 December",
        text: "A ten-day crafts and performing-arts fair at the rural arts village west of the city, drawing artisans from across western India.",
      },
      {
        name: "World Music Festival",
        when: "February",
        text: "Three days of free concerts staged at Gandhi Ground, Fateh Sagar and Ambrai Ghat.",
      },
    ],
    food: [
      "Dal baati churma — eaten here with a sharper, garlic-heavy mirchi chutney",
      "Mewari kachori and mirchi bada — the standard Udaipur breakfast",
      "Gatte ki sabzi and ker sangri — the Marwari vegetarian canon",
      "Laal maas and safed maas — Mewar's two great mutton curries, one red with chillies, one white with cashew and cream",
      "Malpua with rabri — dense, syrup-soaked, best in winter",
      "Masala chai at a ghat-side stall, which costs almost nothing and is half the experience",
    ],
    practical: [
      { label: "Nearest airport", value: "Maharana Pratap (UDR), 22 km — direct from Delhi, Mumbai, Jaipur" },
      { label: "By rail", value: "Udaipur City station — Delhi ~12 h overnight · Jaipur 7 h · Ahmedabad 5 h" },
      { label: "By road", value: "Jaipur 395 km (6 h) · Jodhpur 250 km · Ahmedabad 260 km · Jawai 160 km" },
      { label: "Getting around", value: "Old city on foot; autos elsewhere. Boats from Rameshwar Ghat for the islands." },
      { label: "Typical stay", value: "3 nights, or 4 with a Kumbhalgarh–Ranakpur day trip" },
      { label: "Where to stay", value: "Lal Ghat and Hanuman Ghat for views; Fateh Sagar for quiet" },
    ],
    mindful:
      "The lakes are rain-fed and periodically run dry, and the old city's drainage flows into them. Choose accommodation that treats its waste water, skip the plastic bottle, and don't feed the fish or birds from the boats.",
  },
  {
    id: "jawai",
    title: "Jawai Bandh",
    subtitle: "Leopard Hills & Dam",
    tagline: "Granite kopjes, a reservoir full of flamingos, and leopards that live beside people.",
    hero: "images/jawai.jpg",
    heroFocus: "center 52%",
    heroCredit: "Granite kopjes above the Jawai reservoir",
    accent: "#c97b4a",
    accentDeep: "#5d3218",
    lede: "Jawai is not a national park. There are no fences, no core zone, no buffer — just two billion years of weathered granite rising out of farmland and scrub, a dam built in the 1950s, villages of Rabari herders, and one of the densest populations of free-ranging leopards anywhere on earth. The leopards sleep in caves in the rocks by day and walk through the fields at night, past goats, past temples, past people. Almost nobody gets hurt. That arrangement, more than the wildlife itself, is what makes the place remarkable.",
    stats: [
      { label: "Dam built", value: "1946 – 1957" },
      { label: "Commissioned by", value: "Maharaja Umaid Singh of Jodhpur" },
      { label: "Rock age", value: "~2 billion years, Precambrian granite" },
      { label: "Leopards", value: "Roughly 50–70 in the core belt" },
      { label: "Conservation reserve", value: "Notified 2017, ~19,000 ha" },
      { label: "Best season", value: "October – March" },
    ],
    sections: [
      {
        heading: "The rock came first",
        body: [
          "The kopjes at Jawai are inselbergs — isolated domes of Precambrian granite, part of the Aravalli system and among the oldest exposed rock on the Indian subcontinent. Softer material around them eroded away over hundreds of millions of years, leaving smooth boulders stacked and split into caves, ledges and overhangs.",
          "Those cavities are the reason leopards are here in such numbers. A granite cave stays cool through a 45 °C afternoon, is defensible, and gives a mother a place to leave cubs while she hunts. From the top of a kopje a leopard can see every approach for kilometres.",
          "The hills also carry shrines. Many caves hold small temples — to Ashapura Mata, to Shiva — and are visited by villagers who walk up alone, sometimes past a sleeping leopard. The overlap of sacred space and predator den is not incidental to how this coexistence works.",
        ],
      },
      {
        heading: "A dam, and what it brought",
        body: [
          "Jawai Bandh was commissioned by Maharaja Umaid Singh of Jodhpur and built between 1946 and 1957 across the Jawai river, a tributary of the Luni. It remains the largest dam in western Rajasthan, holding around 7,300 million cubic feet at capacity, and supplies drinking water to Pali and Jodhpur along with irrigation for the surrounding district.",
          "The reservoir turned a dry belt into a wetland. In winter the shallows fill with migratory birds — greater and lesser flamingos, bar-headed geese, demoiselle cranes, painted storks, spoonbills, pelicans — and the water holds a resident population of marsh mugger crocodiles that bask on the banks in the middle of the day.",
          "It also brought farming, and with it goats, and with goats a reliable food supply for leopards. The ecology at Jawai is frankly artificial in origin, and it works.",
        ],
      },
      {
        heading: "The Rabari",
        body: [
          "The Rabari are a semi-nomadic pastoralist community, traditionally camel and goat herders, and they have shared this landscape with leopards for as long as anyone can document. The men wear red turbans and white dhotis and carry a staff; many still walk their herds long distances on seasonal migration.",
          "They do not hunt leopards, and they rarely retaliate when one takes a goat. The prevailing belief is that the leopards are attached to the deities in the hill shrines — guardians rather than vermin — and that a life lived alongside them is simply the arrangement. Compensation schemes exist for livestock losses, but the tolerance predates them by centuries.",
          "The result is a place with functionally no human-leopard conflict in a district where the two species overlap completely. Conservation biologists come to Jawai to study exactly this, because it contradicts most of what the field assumes about large carnivores near people.",
        ],
      },
      {
        heading: "How a Jawai safari actually works",
        body: [
          "Drives go out twice a day, around 6 a.m. and again at about 4 p.m., in open 4x4s, on village tracks and dry riverbeds rather than park roads. There is no ticketed gate and no fixed route; guides work the kopjes they know, glassing the ledges for a shape that resolves into a cat.",
          "Sightings are genuinely good — most visitors on a two-night stay see a leopard, and many see several — but this is not a guaranteed-tiger-reserve experience. Expect to spend time watching sloth bear, striped hyena, jungle cat, chinkara, nilgai, desert fox and an outstanding range of raptors while you wait.",
          "Because the land is unfenced and largely private or common grazing, etiquette matters more than elsewhere: no off-roading across crops, no crowding a cat, no spotlights on animals, and no more than a couple of vehicles at a sighting. Operators who ignore this are the main threat to the place.",
        ],
      },
    ],
    highlights: [
      {
        name: "Leopard Hill",
        meta: "Core sighting area",
        text: "The cluster of kopjes around the Jawai Bandh temple where the resident leopards are most reliably found at dawn and dusk.",
      },
      {
        name: "Jawai reservoir",
        meta: "Winter birding",
        text: "Flamingos in the shallows from November, plus cranes, storks and pelicans, with mugger crocodiles on the banks year round.",
      },
      {
        name: "Devgiri & Perwa caves",
        meta: "Granite shrines",
        text: "Hill temples inside leopard territory, reached on foot. Go with a guide and go early.",
      },
      {
        name: "Rabari settlements",
        meta: "Village visits",
        text: "Arranged through camps rather than turning up unannounced. Ask before photographing anyone.",
      },
      {
        name: "Bera",
        meta: "The village at the centre of it",
        text: "The name many operators still use for the whole belt, and the base for some of the earliest leopard-watching here.",
      },
      {
        name: "Sunset on the rocks",
        meta: "Evening",
        text: "Camps set up drinks on a granite shoulder facing west. The rock holds the day's heat and the kopjes go rust-red.",
      },
    ],
    experiences: [
      {
        name: "Two safaris a day",
        meta: "Dawn and late afternoon",
        text: "Three to four hours each, in an open jeep. Nights are cold from December — the camps supply blankets and hot water bottles.",
      },
      {
        name: "Walk with a Rabari herder",
        meta: "2 hours",
        text: "The most valuable thing you can do here. You learn more about the leopards from someone who shares a hillside with them than from any hide.",
      },
      {
        name: "Birding the dam edge",
        meta: "Early morning",
        text: "Over 100 species recorded around the reservoir in winter. Bring binoculars; the camps' spotting scopes are usually on the jeeps.",
      },
      {
        name: "Night sky",
        meta: "After dinner",
        text: "No significant light pollution for tens of kilometres. The Milky Way is visible to the naked eye most clear nights.",
      },
    ],
    seasons: [
      {
        months: "Nov – Feb",
        label: "Prime",
        text: "Cool days, cold mornings, peak bird numbers and comfortable safari conditions. Book well ahead — bed capacity here is small.",
      },
      {
        months: "Oct & Mar",
        label: "Excellent",
        text: "Warmer, quieter, still very good sightings. Shoulder rates at most camps.",
      },
      {
        months: "Apr – Jun",
        label: "Hot but productive",
        text: "Brutally hot by midday, but animals concentrate around the remaining water, which makes sightings more predictable.",
      },
      {
        months: "Jul – Sep",
        label: "Monsoon",
        text: "Many camps close. Tracks flood, the granite turns green with moss, and the reservoir refills.",
      },
    ],
    festivals: [
      {
        name: "Nag Panchami at the hill shrines",
        when: "July – August",
        text: "Villagers walk up to the cave temples in the kopjes — the clearest expression of why these hills are treated as sacred ground.",
      },
      {
        name: "Rabari migration",
        when: "Post-monsoon",
        text: "Not a festival, but the seasonal movement of herds across the district is the district's real calendar.",
      },
      {
        name: "Navratri",
        when: "September – October",
        text: "Nine nights of garba and shrine offerings in the surrounding villages, including at Ashapura Mata temples in the rocks.",
      },
    ],
    food: [
      "Bajra roti with ghee and gur — the working staple of the herding villages",
      "Ker sangri — desert beans and berries, at their best in this belt",
      "Gatte ki sabzi and papad ki sabzi — Marwari kitchen improvisations for a place with no vegetables",
      "Rabari — the thick set curd the community is named for, eaten with bajra",
      "Camp cooking, which at the better properties means open-fire Marwari food served in the riverbed",
    ],
    practical: [
      { label: "Nearest airport", value: "Udaipur (UDR) 160 km · Jodhpur (JDH) 160 km" },
      { label: "By rail", value: "Jawai Bandh or Mori Bera station, Ahmedabad–Jodhpur line" },
      { label: "By road", value: "Udaipur 3 h · Jodhpur 3 h · Ranakpur 1.5 h · Mount Abu 2.5 h" },
      { label: "Getting around", value: "Camp jeeps only. There is no public transport to the sighting areas." },
      { label: "Typical stay", value: "2 nights minimum — four safari slots is the realistic number for a good sighting" },
      { label: "What to bring", value: "Neutral clothing, warm layers for dawn, binoculars, a 300 mm lens or longer" },
    ],
    mindful:
      "Jawai's leopards live on unfenced common land beside working farms. Never ask a driver to go off-track or to crowd a cat, keep noise down, don't use flash or spotlights, and choose operators who cap vehicles at a sighting. The coexistence here is fragile and entirely dependent on the Rabari continuing to tolerate the animals.",
  },
];

export function getPlace(id: string | undefined): Place | undefined {
  return places.find((p) => p.id === id);
}
