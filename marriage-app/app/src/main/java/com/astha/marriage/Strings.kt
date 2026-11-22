package com.astha.marriage

import androidx.compose.runtime.staticCompositionLocalOf
import com.astha.marriage.engine.PointLabel

enum class Language { EN, NE }

/** All text shown in the app, in one language. */
interface Strings {
    val appTitle: String
    val subtitle: String
    val play: String
    val rules: String
    val players: String
    val language: String
    val you: String
    val botNames: List<String>
    val back: String
    val deck: String
    val discard: String
    val joker: String
    val jokerHidden: String
    val yourTurnDraw: String
    val yourTurnPlay: String
    fun waitingFor(name: String): String
    val exposeTunnela: String
    val showSets: String
    val showDublees: String
    val finish: String
    val throwCard: String
    val selectToThrow: String
    val sortSuit: String
    val sortRank: String
    val seen: String
    val notSeen: String
    fun cards(n: Int): String
    val cannotTakeJoker: String
    val dubleeOnlyToWin: String
    val cannotThrowTaken: String
    val cannotFinish: String
    val needThreePure: String
    fun drewStock(name: String): String
    fun tookDiscard(name: String, card: String): String
    fun threw(name: String, card: String): String
    fun exposed(name: String, card: String): String
    fun showedSets(name: String): String
    fun showedDublees(name: String): String
    fun won(name: String): String
    val reshuffled: String
    val noWinner: String
    val handOver: String
    fun winnerIs(name: String): String
    val byDublees: String
    val tiplu: String
    val points: String
    val thisHand: String
    val total: String
    val winningHand: String
    val nextHand: String
    val home: String
    fun handNumber(n: Int): String
    val scores: String
    val laidDown: String
    val nothingLaid: String
    val close: String
    val quitConfirm: String
    val yes: String
    val no: String
    fun pointLabel(label: PointLabel): String
    val rulesSections: List<Pair<String, String>>
}

object English : Strings {
    override val appTitle = "Marriage"
    override val subtitle = "The Nepali card game"
    override val play = "Play"
    override val rules = "Rules"
    override val players = "Players"
    override val language = "भाषा / Language"
    override val you = "You"
    override val botNames = listOf("Ram", "Sita", "Hari", "Gita")
    override val back = "Back"
    override val deck = "Deck"
    override val discard = "Discard"
    override val joker = "Joker"
    override val jokerHidden = "Hidden"
    override val yourTurnDraw = "Your turn: take a card from the deck or the discard"
    override val yourTurnPlay = "Select a card to throw"
    override fun waitingFor(name: String) = "$name is playing…"
    override val exposeTunnela = "Show tunnela"
    override val showSets = "See joker"
    override val showDublees = "See (7 dublee)"
    override val finish = "Finish!"
    override val throwCard = "Throw"
    override val selectToThrow = "Tap a card to select it"
    override val sortSuit = "By suit"
    override val sortRank = "By rank"
    override val seen = "Seen"
    override val notSeen = "Not seen"
    override fun cards(n: Int) = "$n cards"
    override val cannotTakeJoker = "You have seen the joker, so you can't pick up a joker card"
    override val dubleeOnlyToWin = "Dublee players can only pick up a card that completes the 8th dublee"
    override val cannotThrowTaken = "You can't throw the card you just picked up"
    override val cannotFinish = "Your cards don't make 7 combinations yet"
    override val needThreePure = "You need 3 pure sequences or tunnelas"
    override fun drewStock(name: String) = "$name drew from the deck"
    override fun tookDiscard(name: String, card: String) = "$name picked up $card"
    override fun threw(name: String, card: String) = "$name threw $card"
    override fun exposed(name: String, card: String) = "$name showed a tunnela of $card"
    override fun showedSets(name: String) = "$name showed 3 sets and saw the joker"
    override fun showedDublees(name: String) = "$name showed 7 dublees and saw the joker"
    override fun won(name: String) = "$name finished the game!"
    override val reshuffled = "The discards were shuffled into a new deck"
    override val noWinner = "The cards ran out. Nobody won this hand."
    override val handOver = "Hand over"
    override fun winnerIs(name: String) = "$name won"
    override val byDublees = "with 8 dublees"
    override val tiplu = "Tiplu"
    override val points = "Maal"
    override val thisHand = "This hand"
    override val total = "Total"
    override val winningHand = "Winning hand"
    override val nextHand = "Next hand"
    override val home = "Home"
    override fun handNumber(n: Int) = "Hand $n"
    override val scores = "Scores"
    override val laidDown = "Cards on the table"
    override val nothingLaid = "Nothing shown yet"
    override val close = "Close"
    override val quitConfirm = "Leave this game? The scores will be lost."
    override val yes = "Yes"
    override val no = "No"
    override fun pointLabel(label: PointLabel) = when (label) {
        PointLabel.MARRIAGE -> "Marriage"
        PointLabel.TIPLU -> "Tiplu"
        PointLabel.POPLU -> "Poplu"
        PointLabel.JHIPLU -> "Jhiplu"
        PointLabel.ALTER -> "Alter"
        PointLabel.TUNNELA_ORDINARY -> "Tunnela"
        PointLabel.TUNNELA_JOKER -> "Joker tunnela"
        PointLabel.TUNNELA_POPLU -> "Poplu tunnela"
        PointLabel.TUNNELA_JHIPLU -> "Jhiplu tunnela"
        PointLabel.TUNNELA_ALTER -> "Alter tunnela"
    }

    override val rulesSections = listOf(
        "Goal" to "Each player gets 21 cards from three decks. Arrange all 21 into 7 combinations of 3 cards, or collect 8 dublees (pairs of identical cards).",
        "Combinations" to "• Tunnela: 3 identical cards (same rank and suit).\n• Pure sequence: 3 cards in a row of one suit. Ace can be high (Q-K-A) or low (A-2-3), but K-A-2 is not allowed.\n• Triplet: 3 cards of the same rank, all different suits.\n• Dirty sequence or triplet: made with jokers. Two identical cards plus a joker is not allowed.",
        "Your turn" to "Take the top card of the deck or the card the previous player just threw. Then throw one card. You can't throw the card you just picked up.",
        "Seeing the joker" to "Lay down 3 pure sequences or tunnelas to see the joker. The first player to do this picks the tiplu. Every card of the tiplu's rank is a joker, and so are the poplu (one rank above, same suit) and the jhiplu (one rank below, same suit). The alter has the same rank and colour as the tiplu but the other suit. After you have seen, you can't pick up a joker from the discard pile.",
        "Tunnela at the start" to "If you are dealt a tunnela, you can show it before your first draw. It counts towards seeing the joker and scores points at the end.",
        "Dublees" to "Instead of combinations, collect pairs of identical cards. With 7 dublees you can see the joker; with 8 you win. Jokers can't be used in dublees. After seeing, you may pick up a discard only if it completes your 8th dublee.",
        "Finishing" to "After seeing, if your cards make 4 more combinations (7 in all), press Finish. The last card is thrown and the hand ends.",
        "Maal points" to "Only players who have seen score.\n• Tiplu 3 (two: 7)\n• Poplu or jhiplu 2 (two: 5, three: 10)\n• Alter 5 (two: 15, three: 35)\n• Marriage (jhiplu + tiplu + poplu) 10 (two: 30)\n• Tunnela shown at the start: 5, joker tunnela 10, poplu/jhiplu tunnela 20, alter tunnela 35",
        "Payments" to "Each player pays the winner 3 if they have seen the joker, or 10 if they have not. A dublee win earns 5 more from everyone. Then every pair of players settles the difference in their maal points.",
    )
}

object Nepali : Strings {
    override val appTitle = "म्यारिज"
    override val subtitle = "नेपाली तास खेल"
    override val play = "खेल्नुहोस्"
    override val rules = "नियमहरू"
    override val players = "खेलाडी"
    override val language = "भाषा / Language"
    override val you = "तपाईं"
    override val botNames = listOf("राम", "सीता", "हरि", "गीता")
    override val back = "पछाडि"
    override val deck = "तास"
    override val discard = "फालिएको"
    override val joker = "जोकर"
    override val jokerHidden = "लुकेको"
    override val yourTurnDraw = "तपाईंको पालो: तासबाट वा फालिएको पत्ता तान्नुहोस्"
    override val yourTurnPlay = "फाल्ने पत्ता छान्नुहोस्"
    override fun waitingFor(name: String) = "$name खेल्दै…"
    override val exposeTunnela = "टनेला देखाउनुहोस्"
    override val showSets = "जोकर हेर्नुहोस्"
    override val showDublees = "हेर्नुहोस् (७ डबली)"
    override val finish = "जित्नुहोस्!"
    override val throwCard = "फाल्नुहोस्"
    override val selectToThrow = "पत्ता छान्न थिच्नुहोस्"
    override val sortSuit = "रङ अनुसार"
    override val sortRank = "अंक अनुसार"
    override val seen = "देखेको"
    override val notSeen = "नदेखेको"
    override fun cards(n: Int) = "$n पत्ता"
    override val cannotTakeJoker = "तपाईंले जोकर देखिसक्नुभयो, त्यसैले जोकर पत्ता उठाउन पाइँदैन"
    override val dubleeOnlyToWin = "डबली खेलाडीले ८औं डबली पूरा हुने पत्ता मात्र उठाउन पाउँछ"
    override val cannotThrowTaken = "भर्खरै उठाएको पत्ता फाल्न पाइँदैन"
    override val cannotFinish = "तपाईंका पत्ताले अझै ७ वटा जोडी बनाउँदैनन्"
    override val needThreePure = "३ वटा शुद्ध सिक्वेन्स वा टनेला चाहिन्छ"
    override fun drewStock(name: String) = "$name ले तासबाट तान्यो"
    override fun tookDiscard(name: String, card: String) = "$name ले $card उठायो"
    override fun threw(name: String, card: String) = "$name ले $card फाल्यो"
    override fun exposed(name: String, card: String) = "$name ले $card को टनेला देखायो"
    override fun showedSets(name: String) = "$name ले ३ सेट देखाएर जोकर हेर्यो"
    override fun showedDublees(name: String) = "$name ले ७ डबली देखाएर जोकर हेर्यो"
    override fun won(name: String) = "$name ले खेल जित्यो!"
    override val reshuffled = "फालिएका पत्ता फिटेर नयाँ तास बनाइयो"
    override val noWinner = "तास सकियो। यो हात कसैले जितेन।"
    override val handOver = "हात सकियो"
    override fun winnerIs(name: String) = "$name ले जित्यो"
    override val byDublees = "८ डबलीसहित"
    override val tiplu = "टिप्लु"
    override val points = "माल"
    override val thisHand = "यो हात"
    override val total = "जम्मा"
    override val winningHand = "जित्ने हात"
    override val nextHand = "अर्को हात"
    override val home = "गृहपृष्ठ"
    override fun handNumber(n: Int) = "हात $n"
    override val scores = "अंक"
    override val laidDown = "टेबलमा राखिएका पत्ता"
    override val nothingLaid = "अहिलेसम्म केही देखाइएको छैन"
    override val close = "बन्द गर्नुहोस्"
    override val quitConfirm = "यो खेल छोड्ने? अंकहरू हराउनेछन्।"
    override val yes = "हो"
    override val no = "होइन"
    override fun pointLabel(label: PointLabel) = when (label) {
        PointLabel.MARRIAGE -> "म्यारिज"
        PointLabel.TIPLU -> "टिप्लु"
        PointLabel.POPLU -> "पोप्लु"
        PointLabel.JHIPLU -> "झिप्लु"
        PointLabel.ALTER -> "अल्टर"
        PointLabel.TUNNELA_ORDINARY -> "टनेला"
        PointLabel.TUNNELA_JOKER -> "जोकर टनेला"
        PointLabel.TUNNELA_POPLU -> "पोप्लु टनेला"
        PointLabel.TUNNELA_JHIPLU -> "झिप्लु टनेला"
        PointLabel.TUNNELA_ALTER -> "अल्टर टनेला"
    }

    override val rulesSections = listOf(
        "लक्ष्य" to "तीन गड्डी तासबाट हरेक खेलाडीले २१ पत्ता पाउँछ। सबै २१ पत्तालाई ३-३ पत्ताका ७ वटा जोडीमा मिलाउनुहोस्, वा ८ वटा डबली (उस्तै दुई पत्ताको जोडी) जम्मा गर्नुहोस्।",
        "जोडीहरू" to "• टनेला: उस्तै ३ पत्ता (एउटै अंक र रङ)।\n• शुद्ध सिक्वेन्स: एउटै रङका लगातार ३ पत्ता। एक्का माथि (Q-K-A) वा तल (A-2-3) हुन सक्छ, तर K-A-2 मान्य छैन।\n• ट्रायल: एउटै अंकका ३ पत्ता, सबै फरक रङका।\n• जोकरसहितको सिक्वेन्स वा ट्रायल: जोकर प्रयोग गरेर बनाइन्छ। उस्तै दुई पत्ता र एउटा जोकर मान्य छैन।",
        "तपाईंको पालो" to "तासको माथिल्लो पत्ता वा अघिल्लो खेलाडीले भर्खर फालेको पत्ता उठाउनुहोस्। त्यसपछि एउटा पत्ता फाल्नुहोस्। भर्खरै उठाएको पत्ता फाल्न पाइँदैन।",
        "जोकर हेर्ने" to "जोकर हेर्न ३ वटा शुद्ध सिक्वेन्स वा टनेला टेबलमा राख्नुहोस्। पहिलो खेलाडीले टिप्लु छान्छ। टिप्लुको अंकका सबै पत्ता जोकर हुन्, साथै पोप्लु (एउटै रङको एक अंक माथि) र झिप्लु (एउटै रङको एक अंक तल) पनि। अल्टर भनेको टिप्लुकै अंक र रङ्गको तर अर्को चिह्नको पत्ता हो। जोकर हेरिसकेपछि फालिएको जोकर उठाउन पाइँदैन।",
        "सुरुको टनेला" to "बाँड्दा नै टनेला आएमा पहिलो पालो अघि देखाउन सकिन्छ। यो जोकर हेर्न गनिन्छ र अन्त्यमा अंक पाउँछ।",
        "डबली" to "जोडीको सट्टा उस्तै पत्ताका जोडी जम्मा गर्नुहोस्। ७ डबलीमा जोकर हेर्न पाइन्छ, ८ मा जित। डबलीमा जोकर चल्दैन। जोकर हेरिसकेपछि ८औं डबली पूरा हुने भए मात्र फालिएको पत्ता उठाउन पाइन्छ।",
        "जित्ने" to "जोकर हेरिसकेपछि तपाईंका पत्ताले थप ४ जोडी (जम्मा ७) बनाए भने 'जित्नुहोस्' थिच्नुहोस्। अन्तिम पत्ता फालिन्छ र हात सकिन्छ।",
        "माल अंक" to "जोकर देखेका खेलाडीले मात्र अंक पाउँछन्।\n• टिप्लु ३ (दुई: ७)\n• पोप्लु वा झिप्लु २ (दुई: ५, तीन: १०)\n• अल्टर ५ (दुई: १५, तीन: ३५)\n• म्यारिज (झिप्लु + टिप्लु + पोप्लु) १० (दुई: ३०)\n• सुरुमा देखाएको टनेला: ५, जोकर टनेला १०, पोप्लु/झिप्लु टनेला २०, अल्टर टनेला ३५",
        "भुक्तानी" to "जोकर देखेका खेलाडीले जित्नेलाई ३ र नदेखेकाले १० तिर्छन्। डबलीले जितेमा सबैले थप ५ तिर्छन्। त्यसपछि हरेक दुई खेलाडीबीच मालको फरक मिलाइन्छ।",
    )
}

fun stringsFor(language: Language): Strings = if (language == Language.NE) Nepali else English

val LocalStrings = staticCompositionLocalOf<Strings> { English }
