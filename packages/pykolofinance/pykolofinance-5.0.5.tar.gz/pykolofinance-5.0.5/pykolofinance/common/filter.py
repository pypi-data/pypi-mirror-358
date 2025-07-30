from datetime import datetime, time

import django_filters


class BaseFilterSet(django_filters.FilterSet):

    def __init__(self, data=None, *args, **kwargs):
        # if filterset is bound, use initial values as defaults
        if data is not None:
            # get a mutable copy of the QueryDict
            data = data.copy()

            for name, f in self.base_filters.items():
                initial = f.extra.get('initial')

                # filter param is either missing or empty, use initial as default
                if not data.get(name) and initial:
                    data[name] = initial

        super().__init__(data, *args, **kwargs)


class DateFilter(django_filters.FilterSet):
    start = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    end = django_filters.DateFilter(field_name="created_at", method='filter_end')

    def __init__(self, start_field="created_at", end_field="created_at", **kwargs):
        super().__init__(**kwargs)
        self.start = django_filters.DateFilter(field_name=start_field, lookup_expr="gte")
        self.end = django_filters.DateFilter(field_name=end_field, method='filter_end')

    def filter_end(self, queryset, name, value):
        end_date = datetime.combine(value, time.max)
        f = {f"{name}__lte": end_date}
        return queryset.filter(**f)
