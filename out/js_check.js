const CASES=[{"bed": "coronary", "les": {"d_prox": 3.2, "d_dist": 2.95, "length": 22, "calcium": 0.3, "tortuosity": 0.2, "inflammation": 0.25, "diabetes": true}, "plan": {"device": "des_ultrathin", "nominal_d": 3.0, "length": 28, "prep": "none", "postdilate": false, "n_devices": 1}, "g0": 0.819624, "gend": 0.563887, "tau": 287.183, "deficit": 0.360711, "risk12": 0.014491}, {"bed": "coronary", "les": {"d_prox": 3.0, "d_dist": 2.95, "length": 15, "calcium": 0.15, "tortuosity": 0.2, "inflammation": 0.2, "diabetes": false}, "plan": {"device": "brs_plla", "nominal_d": 3.0, "length": 23, "prep": "scoring", "postdilate": true, "n_devices": 1}, "g0": 0.710588, "gend": 0.598004, "tau": 370.862, "deficit": 0.361738, "risk12": 0.01681}, {"bed": "sfa", "les": {"d_prox": 5.8, "d_dist": 5.2, "length": 150, "calcium": 0.5, "tortuosity": 0.3, "inflammation": 0.25, "runoff": 2}, "plan": {"device": "se_nitinol", "nominal_d": 6.0, "length": 150, "prep": "ivl", "postdilate": false, "n_devices": 1}, "g0": 0.36068, "gend": 0.433174, "tau": 270.43, "deficit": 0.588455, "risk12": 0.097419}, {"bed": "btk", "les": {"d_prox": 2.9, "d_dist": 2.6, "length": 100, "calcium": 0.45, "tortuosity": 0.25, "inflammation": 0.35, "runoff": 1, "diabetes": true}, "plan": {"device": "dcb_periph", "nominal_d": 2.75, "length": 120, "prep": "none", "postdilate": false, "n_devices": 1}, "g0": 0.511093, "gend": 0.072587, "tau": 106.034, "deficit": 0.865272, "risk12": 0.103981}, {"bed": "carotid", "les": {"d_prox": 7.5, "d_dist": 5.0, "length": 20, "calcium": 0.3, "tortuosity": 0.2, "inflammation": 0.2}, "plan": {"device": "car_dual", "nominal_d": 8.0, "length": 30, "prep": "none", "postdilate": true, "n_devices": 1}, "g0": 0.52564, "gend": 0.678655, "tau": 189.474, "deficit": 0.357651, "risk12": 0.006564}];
const out = CASES.map(c => {
  const les = Object.assign({bed:c.bed, stenosis:0.8, diabetes:false, bifurcation:false,
    side_branch:false, cto:false, inflammation:0.2, runoff:3, calcium:0.2,
    tortuosity:0.2}, c.les);
  const r = evaluateCase(les, c.plan, 5, 730);
  const d = (a,b) => +Math.abs(a-b).toExponential(2);
  return {bed:c.bed, dev:c.plan.device,
          dg0:d(r.gamma[0], c.g0),
          dgend:d(r.gamma[r.gamma.length-1], c.gend),
          dtau:d(r.tau_sc, c.tau),
          ddef:d(r.deficit, c.deficit),
          drisk:d(r.risk12, c.risk12)};
});
console.table(out);
