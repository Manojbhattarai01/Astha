package com.astha.marriage.engine

enum class Suit(val symbol: String, val isRed: Boolean) {
    SPADES("♠", false),
    HEARTS("♥", true),
    CLUBS("♣", false),
    DIAMONDS("♦", true),
}

/** Ranks run 1 (ace) to 13 (king). */
object Ranks {
    const val ACE = 1
    const val JACK = 11
    const val QUEEN = 12
    const val KING = 13

    fun label(rank: Int): String = when (rank) {
        ACE -> "A"
        JACK -> "J"
        QUEEN -> "Q"
        KING -> "K"
        else -> rank.toString()
    }

    /** The next rank up, wrapping K → A → 2. */
    fun next(rank: Int): Int = rank % 13 + 1

    /** The next rank down, wrapping 2 → A → K. */
    fun prev(rank: Int): Int = if (rank == 1) 13 else rank - 1
}

/** What a card looks like: two cards with the same face are identical. */
data class Face(val suit: Suit, val rank: Int) {
    init {
        require(rank in 1..13) { "rank must be 1..13" }
    }

    override fun toString(): String = Ranks.label(rank) + suit.symbol
}

/**
 * One physical card. Three decks are used, so [copy] (0..2) tells the three
 * identical copies of a face apart.
 */
data class Card(val face: Face, val copy: Int) {
    val suit: Suit get() = face.suit
    val rank: Int get() = face.rank

    /** Unique id in 0 until 156. */
    val id: Int get() = copy * 52 + suit.ordinal * 13 + (rank - 1)

    override fun toString(): String = face.toString()

    companion object {
        fun of(suit: Suit, rank: Int, copy: Int = 0) = Card(Face(suit, rank), copy)

        /** All 156 cards of three standard decks. */
        fun fullShoe(): List<Card> = buildList {
            for (copy in 0 until 3) for (suit in Suit.entries) for (rank in 1..13) {
                add(Card(Face(suit, rank), copy))
            }
        }
    }
}

/** Kinds of maal (point and wild cards), relative to the tiplu. */
enum class MaalKind { TIPLU, POPLU, JHIPLU, ALTER, ORDINARY_JOKER, NONE }

/**
 * Which cards are wild, as known to one player. [tiplu] is null for a player who
 * has not seen the joker: to them nothing is wild.
 */
data class JokerContext(val tiplu: Face?) {
    fun kind(face: Face): MaalKind {
        val t = tiplu ?: return MaalKind.NONE
        return when {
            face == t -> MaalKind.TIPLU
            face.suit == t.suit && face.rank == Ranks.next(t.rank) -> MaalKind.POPLU
            face.suit == t.suit && face.rank == Ranks.prev(t.rank) -> MaalKind.JHIPLU
            face.rank == t.rank && face.suit.isRed == t.suit.isRed -> MaalKind.ALTER
            face.rank == t.rank -> MaalKind.ORDINARY_JOKER
            else -> MaalKind.NONE
        }
    }

    fun kind(card: Card): MaalKind = kind(card.face)

    fun isWild(card: Card): Boolean = kind(card) != MaalKind.NONE

    companion object {
        val UNSEEN = JokerContext(null)
    }
}
