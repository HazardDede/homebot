{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":train2: |     *Directions* for *${payload.origin}* to *${payload.destination}*  | :train2: "
			}
		},
        {
            "type": "divider"
        }
        %if not payload:
        ,{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No trains"
            }
        }
        %else:
        %for item in payload.connections:
		,{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*${", ".join(item.products)}*: ${item.departure} (+_${item.delay_departure}_) to ${item.arrival} (+_${item.delay_arrival}_) - Total: *${item.travel_time}h*"
			}
		}
        %endfor
        %endif
	]
}