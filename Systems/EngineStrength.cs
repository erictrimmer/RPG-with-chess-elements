using System;

namespace PawnJourney
{
	/// <summary>
	/// How a bot of a given target ELO should play. All tuning lives in the Anchors table below.
	/// These are NOMINAL ratings: they order the bots correctly, but the numbers are only
	/// approximate. Adjust the table after playing the bots yourself.
	/// </summary>
	public readonly struct StrengthSettings
	{
		/// <summary>0 = pick by static evaluation only (no lookahead). N>0 = search N plies.</summary>
		public readonly int Depth;
		/// <summary>Chance (0..1) of playing a uniformly random legal move.</summary>
		public readonly double BlunderChance;
		/// <summary>Pick among root moves within this many centipawns of the best. 0 = always the best move.</summary>
		public readonly int MarginCp;
		/// <summary>Hard time cap for one move, in ms.</summary>
		public readonly int MaxTimeMs;

		public StrengthSettings(int depth, double blunderChance, int marginCp, int maxTimeMs)
		{
			Depth = depth;
			BlunderChance = blunderChance;
			MarginCp = marginCp;
			MaxTimeMs = maxTimeMs;
		}

		public bool IsFullStrength => Depth >= EngineStrength.FullStrengthDepth;

		public override string ToString() =>
			$"depth={Depth} blunder={BlunderChance:0.00} margin={MarginCp}cp maxTime={MaxTimeMs}ms";
	}

	public static class EngineStrength
	{
		/// <summary>Depth value meaning "no cap, search until the time limit".</summary>
		public const int FullStrengthDepth = 64;

		// Elo, depth, blunder chance, margin (cp). Values between anchors are interpolated.
		// Edit this table to retune the whole ladder in one place.
		//
		// How the levers behave (measured by self-play, see Docs/EngineCalibration.md):
		//  - Depth 0 (static evaluation only) is the floor: extra noise barely changes it.
		//  - At depth 1-2, "margin" is a smooth strength dial: each ~50 cp is worth tens of Elo.
		//  - Each extra ply from depth 2 up is worth roughly 100-150 Elo.
		private static readonly (int Elo, int Depth, double Blunder, int Margin)[] Anchors =
		{
			(  100, 0, 0.30, 400),
			(  300, 1, 0.30, 400),
			(  500, 1, 0.13, 280),
			(  700, 1, 0.10, 250),
			(  900, 1, 0.055, 190),
			( 1100, 2, 0.03, 120),
			( 1300, 2, 0.00,  60),
			( 1500, 3, 0.00,  80),
			( 1700, 3, 0.00,  35),
			( 1900, 4, 0.00,   0),
			( 2100, 5, 0.00,  10),
			( 2300, 8, 0.00,   0),
			( 2400, FullStrengthDepth, 0.00, 0),
		};

		/// <summary>Elo at or above which the engine plays at full strength.</summary>
		public static int FullStrengthElo => Anchors[Anchors.Length - 1].Elo;

		/// <param name="elo">Target ELO. Values &lt;= 0 mean "no limit" (full strength).</param>
		/// <param name="fullStrengthTimeMs">Time per move when playing at full strength.</param>
		public static StrengthSettings ForElo(int elo, int fullStrengthTimeMs = 800)
		{
			if (elo <= 0 || elo >= FullStrengthElo)
				return new StrengthSettings(FullStrengthDepth, 0, 0, fullStrengthTimeMs);

			if (elo <= Anchors[0].Elo)
				return Make(Anchors[0]);

			for (int i = 1; i < Anchors.Length; i++)
			{
				if (elo > Anchors[i].Elo) continue;

				var lo = Anchors[i - 1];
				var hi = Anchors[i];
				double t = (elo - lo.Elo) / (double)(hi.Elo - lo.Elo);

				// A step into "full strength" is not interpolated; hold the lower anchor's depth instead.
				int depth = hi.Depth == FullStrengthDepth
					? lo.Depth
					: (int)Math.Round(lo.Depth + t * (hi.Depth - lo.Depth));

				return new StrengthSettings(
					depth,
					Lerp(lo.Blunder, hi.Blunder, t),
					(int)Math.Round(Lerp(lo.Margin, hi.Margin, t)),
					MaxTimeFor(depth));
			}

			return Make(Anchors[Anchors.Length - 1]);
		}

		private static StrengthSettings Make((int Elo, int Depth, double Blunder, int Margin) a) =>
			new StrengthSettings(a.Depth, a.Blunder, a.Margin, MaxTimeFor(a.Depth));

		// Weak bots never need long; this is only a safety net.
		private static int MaxTimeFor(int depth) => depth >= 7 ? 1500 : 1000;

		private static double Lerp(double a, double b, double t) => a + (b - a) * t;
	}
}
