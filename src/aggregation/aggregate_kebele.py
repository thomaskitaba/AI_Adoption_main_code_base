def aggregate_kebele(df, rules):
    return (
        df.groupby(["region", "zone", "woreda", "kebele"])
          .agg(rules)
          .reset_index()
    )
