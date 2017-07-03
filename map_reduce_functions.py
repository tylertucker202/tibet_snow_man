# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 10:01:25 2017

@author: tyler
"""
from bson.code import Code
map_time_series = Code(
    """
    function () {
                var values = {
                    dates: [this.date],
                    };
                emit(this._id, values);
                };
     """)

reduce_time_series = Code(
    """
    function(k,values) {
        var result = {dates: []};
        values.forEach(function(value) {
            var field;
            // append to dates if date exists
            result.dates.push.apply(result.dates,value.dates);
        });
        return result;
       };
       """)
finalize = Code(
    """
    function (key, values) {
        db.temp_coll.save({ _id: key, values: values
        });
        }""")
